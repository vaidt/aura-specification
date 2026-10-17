#!/usr/bin/env python3
"""Read-only diagnostic verifier for armored OpenSSH SSHSIG files.

Usage:
  python verify_sshsig.py GENESIS_DECLARATION.txt AUTHORITY_BINDING_RECORD_v1.1.md

For each PREIMAGE it expects a sibling file named PREIMAGE + ".sig".
This verifies the parsed SSHSIG signed payload with Python cryptography; it is
not a substitute for an end-to-end ssh-keygen -Y verify run.
"""
from __future__ import annotations
import base64
import hashlib
import json
import struct
import sys
from pathlib import Path
from cryptography import __version__ as cryptography_version
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


class ParseError(ValueError):
    pass


def ssh_string(buf: bytes, offset: int) -> tuple[bytes, int]:
    if offset + 4 > len(buf):
        raise ParseError("truncated SSH string length")
    length = struct.unpack(">I", buf[offset:offset + 4])[0]
    offset += 4
    end = offset + length
    if end > len(buf):
        raise ParseError("truncated SSH string")
    return buf[offset:end], end


def encode_ssh_string(value: bytes) -> bytes:
    return struct.pack(">I", len(value)) + value


def git_blob_sha1(payload: bytes) -> str:
    header = b"blob " + str(len(payload)).encode("ascii") + b"\0"
    return hashlib.sha1(header + payload).hexdigest()


def verify(preimage_path: Path) -> dict:
    signature_path = Path(str(preimage_path) + ".sig")
    preimage = preimage_path.read_bytes()
    armour_bytes = signature_path.read_bytes()
    armour_lines = armour_bytes.decode("ascii").strip().splitlines()
    if not armour_lines or armour_lines[0] != "-----BEGIN SSH SIGNATURE-----":
        raise ParseError("missing SSHSIG header")
    if armour_lines[-1] != "-----END SSH SIGNATURE-----":
        raise ParseError("missing SSHSIG footer")
    blob = base64.b64decode("".join(armour_lines[1:-1]), validate=True)

    if len(blob) < 10 or blob[:6] != b"SSHSIG":
        raise ParseError("invalid SSHSIG magic")
    offset = 6
    version = struct.unpack(">I", blob[offset:offset + 4])[0]
    offset += 4
    if version != 1:
        raise ParseError(f"unsupported SSHSIG version: {version}")
    public_key_blob, offset = ssh_string(blob, offset)
    namespace, offset = ssh_string(blob, offset)
    reserved, offset = ssh_string(blob, offset)
    hash_algorithm, offset = ssh_string(blob, offset)
    signature_blob, offset = ssh_string(blob, offset)
    if offset != len(blob):
        raise ParseError("trailing envelope bytes")
    if not namespace:
        raise ParseError("empty SSHSIG namespace")

    key_type, inner = ssh_string(public_key_blob, 0)
    public_key, inner = ssh_string(public_key_blob, inner)
    if inner != len(public_key_blob):
        raise ParseError("trailing public-key bytes")
    signature_type, inner = ssh_string(signature_blob, 0)
    signature, inner = ssh_string(signature_blob, inner)
    if inner != len(signature_blob):
        raise ParseError("trailing signature bytes")
    if key_type != b"ssh-ed25519" or signature_type != b"ssh-ed25519":
        raise ParseError("unexpected public-key/signature algorithm")
    if len(public_key) != 32 or len(signature) != 64:
        raise ParseError("invalid Ed25519 key or signature length")
    if hash_algorithm not in (b"sha256", b"sha512"):
        raise ParseError("unsupported SSHSIG hash algorithm")

    digest = hashlib.new(hash_algorithm.decode("ascii"), preimage).digest()
    signed_payload = (
        b"SSHSIG"
        + encode_ssh_string(namespace)
        + encode_ssh_string(reserved)
        + encode_ssh_string(hash_algorithm)
        + encode_ssh_string(digest)
    )
    Ed25519PublicKey.from_public_bytes(public_key).verify(signature, signed_payload)
    fingerprint = "SHA256:" + base64.b64encode(
        hashlib.sha256(public_key_blob).digest()
    ).decode("ascii").rstrip("=")

    return {
        "preimage_path": str(preimage_path),
        "signature_path": str(signature_path),
        "result": "PASS",
        "preimage_bytes": len(preimage),
        "preimage_sha256": hashlib.sha256(preimage).hexdigest(),
        "preimage_git_blob_sha1": git_blob_sha1(preimage),
        "signature_armour_sha256": hashlib.sha256(armour_bytes).hexdigest(),
        "signature_git_blob_sha1": git_blob_sha1(armour_bytes),
        "decoded_envelope_sha256": hashlib.sha256(blob).hexdigest(),
        "namespace": namespace.decode("ascii"),
        "hash_algorithm": hash_algorithm.decode("ascii"),
        "public_key_type": key_type.decode("ascii"),
        "signature_type": signature_type.decode("ascii"),
        "signature_bytes": len(signature),
        "trailing_envelope_bytes": 0,
        "public_key_fingerprint": fingerprint,
        "python_cryptography_version": cryptography_version,
        "python_ed25519_verification": "PASS",
    }


def main() -> int:
    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        paths = [Path("GENESIS_DECLARATION.txt"),
                 Path("AUTHORITY_BINDING_RECORD_v1.1.md")]
    failures = 0
    results = []
    for path in paths:
        try:
            results.append(verify(path))
        except Exception as exc:
            failures += 1
            results.append({"preimage_path": str(path), "result": "FAIL",
                            "error": f"{type(exc).__name__}: {exc}"})
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
