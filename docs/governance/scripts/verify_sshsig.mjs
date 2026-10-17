#!/usr/bin/env node
// Read-only diagnostic SSHSIG verifier. Each preimage must have a sibling
// file named PREIMAGE + ".sig". This validates the envelope and Ed25519 math
// over the reconstructed payload; also run ssh-keygen -Y verify separately.
import fs from "node:fs";
import crypto from "node:crypto";

function fail(message) { throw new Error(message); }

function parseString(buffer, state) {
  if (state.offset + 4 > buffer.length) fail("truncated SSH string length");
  const length = buffer.readUInt32BE(state.offset);
  state.offset += 4;
  if (state.offset + length > buffer.length) fail("truncated SSH string");
  const result = buffer.subarray(state.offset, state.offset + length);
  state.offset += length;
  return result;
}

function sshString(value) {
  const length = Buffer.alloc(4);
  length.writeUInt32BE(value.length);
  return Buffer.concat([length, value]);
}

function gitBlobSha1(payload) {
  const header = Buffer.from("blob " + payload.length + "\0", "ascii");
  return crypto.createHash("sha1").update(Buffer.concat([header, payload])).digest("hex");
}

function verify(preimagePath) {
  const signaturePath = preimagePath + ".sig";
  const preimage = fs.readFileSync(preimagePath);
  const armourBytes = fs.readFileSync(signaturePath);
  const lines = armourBytes.toString("ascii").trim().split(/\r?\n/);
  if (lines[0] !== "-----BEGIN SSH SIGNATURE-----") fail("missing SSHSIG header");
  if (lines[lines.length - 1] !== "-----END SSH SIGNATURE-----") fail("missing SSHSIG footer");
  const envelope = Buffer.from(lines.slice(1, -1).join(""), "base64");
  const state = { offset: 0 };
  const magic = envelope.subarray(0, 6);
  if (!magic.equals(Buffer.from("SSHSIG"))) fail("invalid SSHSIG magic");
  state.offset = 6;
  if (state.offset + 4 > envelope.length) fail("truncated version");
  const version = envelope.readUInt32BE(state.offset);
  state.offset += 4;
  if (version !== 1) fail("unsupported SSHSIG version");

  const publicKeyBlob = parseString(envelope, state);
  const namespace = parseString(envelope, state);
  const reserved = parseString(envelope, state);
  const hashAlgorithm = parseString(envelope, state);
  const signatureBlob = parseString(envelope, state);
  if (state.offset !== envelope.length) fail("trailing envelope bytes");
  if (namespace.length === 0) fail("empty SSHSIG namespace");
  if (!["sha256", "sha512"].includes(hashAlgorithm.toString("ascii"))) {
    fail("unsupported SSHSIG hash algorithm");
  }

  const publicState = { offset: 0 };
  const keyType = parseString(publicKeyBlob, publicState);
  const publicKey = parseString(publicKeyBlob, publicState);
  if (publicState.offset !== publicKeyBlob.length) fail("trailing public-key bytes");
  const signatureState = { offset: 0 };
  const signatureType = parseString(signatureBlob, signatureState);
  const signature = parseString(signatureBlob, signatureState);
  if (signatureState.offset !== signatureBlob.length) fail("trailing signature bytes");
  if (keyType.toString("ascii") !== "ssh-ed25519" ||
      signatureType.toString("ascii") !== "ssh-ed25519") {
    fail("unexpected public-key/signature algorithm");
  }
  if (publicKey.length !== 32 || signature.length !== 64) {
    fail("invalid Ed25519 key or signature length");
  }

  const algorithm = hashAlgorithm.toString("ascii");
  const digest = crypto.createHash(algorithm).update(preimage).digest();
  const signedPayload = Buffer.concat([
    Buffer.from("SSHSIG"), sshString(namespace), sshString(reserved),
    sshString(hashAlgorithm), sshString(digest)
  ]);
  const spki = Buffer.concat([
    Buffer.from("302a300506032b6570032100", "hex"), publicKey
  ]);
  const key = crypto.createPublicKey({ key: spki, format: "der", type: "spki" });
  if (!crypto.verify(null, signedPayload, key, signature)) {
    fail("Ed25519 signature verification failed");
  }

  return {
    preimage_path: preimagePath,
    signature_path: signaturePath,
    result: "PASS",
    preimage_bytes: preimage.length,
    preimage_sha256: crypto.createHash("sha256").update(preimage).digest("hex"),
    preimage_git_blob_sha1: gitBlobSha1(preimage),
    signature_armour_sha256: crypto.createHash("sha256").update(armourBytes).digest("hex"),
    signature_git_blob_sha1: gitBlobSha1(armourBytes),
    decoded_envelope_sha256: crypto.createHash("sha256").update(envelope).digest("hex"),
    namespace: namespace.toString("ascii"),
    hash_algorithm: algorithm,
    public_key_type: keyType.toString("ascii"),
    signature_type: signatureType.toString("ascii"),
    signature_bytes: signature.length,
    trailing_envelope_bytes: 0,
    public_key_fingerprint: "SHA256:" +
      crypto.createHash("sha256").update(publicKeyBlob).digest("base64").replace(/=+$/, ""),
    node_version: process.version,
    node_ed25519_verification: "PASS"
  };
}

const paths = process.argv.slice(2);
if (paths.length === 0) {
  paths.push("GENESIS_DECLARATION.txt", "AUTHORITY_BINDING_RECORD_v1.1.md");
}
let failures = 0;
const results = [];
for (const path of paths) {
  try { results.push(verify(path)); }
  catch (error) {
    failures++;
    results.push({ preimage_path: path, result: "FAIL", error: String(error) });
  }
}
console.log(JSON.stringify(results, null, 2));
if (failures) process.exitCode = 1;
