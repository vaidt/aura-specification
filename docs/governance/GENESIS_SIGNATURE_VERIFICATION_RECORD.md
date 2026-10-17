# Genesis Signature Verification Record

**Document ID:** AURA-GSVR-001  
**Version:** 0.1-DRAFT  
**Status:** DRAFT · NON-CONSTITUTIVE · NOT RATIFIED  
**Normative effect:** NONE  
**Review date:** 2026-10-17  
**Repository:** `vaidt/aura-specification`  
**Observed source ref:** `main` at `8f0cd6be94a68a3728e69a1d21d49237c9d8bd05`

> This record reports technical observations about specific repository bytes. It does not establish a real-world identity, authority to issue a constitutional act, or normative effectiveness.

## 1. Executive disposition

| Claim | Result | Boundary |
|---|---|---|
| Genesis preimage bytes match the repository object | **PASS** | Exact Git blob identity and SHA-256 reproduced |
| SSHSIG envelope structure | **PASS BY TWO LOCAL PARSERS** | Version 1, expected field lengths, supported algorithm names, no trailing bytes |
| Ed25519 signature mathematics | **PASS** | Python `cryptography`, OpenSSL CLI and Node.js verify the reconstructed SSHSIG signed payload; see backend-independence caveat in §4 |
| Key used by Genesis signature matches the key in Authority Binding v1.1 | **PASS** | Same SSH public-key blob / SHA-256 fingerprint |
| Canonical OpenSSH `ssh-keygen -Y verify` end-to-end invocation | **NOT RUN** | `ssh-keygen` is not installed in the audit environment |
| Signature creation time of 2026-09-24 | **NOT ESTABLISHED BY THE SIGNATURE** | SSHSIG contains no signing-time field |
| Real-world identity of the key holder | **NOT ESTABLISHED BY CRYPTOGRAPHY ALONE** | The signed Authority Binding record uses the same key and is not an independent identity anchor |
| Key not revoked | **NOT ESTABLISHED** | No revocation artefact/list was found in the reviewed repository tree; absence is not proof of non-revocation |
| Constitutional competence or Article XIII effectiveness | **NOT ESTABLISHED** | Outside the cryptographic verification claim |
| Overall G1 | **BLOCKED** | Cryptographic sub-check passes; authority/procedure sub-check remains unresolved |

## 2. Frozen evidence references

The following GitHub Content API blob identifiers were read back from `main` and matched to the reconstructed local byte streams using Git's blob-object hash:

| Artefact | Git blob SHA-1 | SHA-256 of file bytes |
|---|---|---|
| `GENESIS_DECLARATION.txt` | `9c19e97270a4539ea7788a0553db2a800a573c44` | `6b5a4c4eaa258eef27452fe6a2f2d752484ae6c88968a039b0b40ca0ac8f2bb6` |
| `GENESIS_DECLARATION.txt.sig` | `82f114a695c5b30094500452c8770cb4d6d572f5` | `154f34a66e57cf5a9af1e83a6747fd925cf3f5b2a8e0bc7291eebf2e4b3acb15` |
| `allowed_signers` | `fa4fa29ed870f350f38157e9a1e15fe9654a6f86` | Not used as a trust anchor by this record |
| `AUTHORITY_BINDING_RECORD_v1.1.md` | `f9dbbcc138a2e0d1bdb34aea2a238394a28ed2cd` | `9544bee7bb3a042cac5041deb73706832c04c5d0e83f5c01252c71e839e678f0` |
| `AUTHORITY_BINDING_RECORD_v1.1.md.sig` | `eed7842fc54f5bfeaaafecca63f5dfbe24823b79` | `2c7968dbdfe3153a24f0aeb2316e922f3c8e8bf4d106c8710863b1fcd8598c67` |

Additional SHA-256 digests:
- Decoded Genesis SSHSIG envelope: `c8d2f729db57b3720b5e801b1a0973cb2bba4866e9d3c010ed3e8e286847db63`.
- Decoded Authority Binding SSHSIG envelope: `837c1be6c64dcd95a11c1fa64f600d12aeae995b30d191093fd4918a56e09093`.

The Genesis preimage's SHA-256 matches the value referenced by `AURA_M1_CLOSURE_RECORD_v1.0.md`. The local byte domain reproduced the GitHub blob object exactly for both the declaration and detached signature; this was not inferred from a rendered GitHub page alone.

## 3. SSHSIG structural inspection

The detached signature was decoded from its armour and parsed as an OpenSSH SSH Signature (SSHSIG) object. Independently implemented parsers in Python and Node.js reported the same fields:

| Field | Genesis declaration | Authority Binding v1.1 |
|---|---|---|
| Magic | `SSHSIG` | `SSHSIG` |
| Version | `1` | `1` |
| Public-key algorithm | `ssh-ed25519` | `ssh-ed25519` |
| Namespace | `aura-genesis` | `aura-governance` |
| Reserved field | empty | empty |
| Preimage hash algorithm | `sha512` | `sha512` |
| Signature algorithm | `ssh-ed25519` | `ssh-ed25519` |
| Raw Ed25519 signature length | 64 bytes | 64 bytes |
| Trailing envelope bytes | 0 | 0 |
| Public-key fingerprint | `SHA256:u9HaNYWZGQYvGET5ZaX2c/V56MzL0Xo7Ilg9M1pZRwU` | same |

The key blob extracted from each signature is identical to the public key embedded in `AUTHORITY_BINDING_RECORD_v1.1.md` and the key configured in `allowed_signers`. This establishes cryptographic key continuity between these repository artefacts, not an independent identity or authority chain.

OpenSSH's `PROTOCOL.sshsig` describes the SSHSIG envelope and signed-data construction. RFC 8709 defines the `ssh-ed25519` public-key/signature encoding; it is not, by itself, a timestamping mechanism or proof of constitutional authority:
- https://github.com/openssh/openssh-portable/blob/master/PROTOCOL.sshsig
- https://www.rfc-editor.org/rfc/rfc8709.html

## 4. Independent mathematical verification

The signed payload was reconstructed from the SSHSIG fields using the documented construction: the SSHSIG preamble, namespace, reserved field, hash algorithm, and the specified digest of the exact preimage.

Observed environment:
- Python `cryptography`: 46.0.4
- OpenSSL: 3.5.5 (27 Jan 2026)
- Node.js: v22.16.0
- OpenSSH `ssh-keygen`: unavailable in the environment

Observed results for `GENESIS_DECLARATION.txt`:
- Python `Ed25519PublicKey.verify(signature, signed_payload)`: **PASS**
- OpenSSL `pkeyutl -verify -pubin -inkey genesis_pubkey.pem -rawin -in signed_payload.bin -sigfile raw_signature.bin`: **Signature Verified Successfully**, exit code 0
- Node.js `crypto.verify(null, signedPayload, publicKey, signature)`: **PASS**

Observed results for `AUTHORITY_BINDING_RECORD_v1.1.md`:
- Python `Ed25519PublicKey.verify(signature, signed_payload)`: **PASS**
- OpenSSL `pkeyutl -verify -pubin -inkey genesis_pubkey.pem -rawin -in signed_payload.bin -sigfile raw_signature.bin`: **Signature Verified Successfully**, exit code 0
- Node.js `crypto.verify(null, signedPayload, publicKey, signature)`: **PASS**

The Node.js verifier independently parsed the SSHSIG envelope, rejected unsupported/malformed fields and trailing bytes, reconstructed the signed payload, and then verified the Ed25519 signature. OpenSSL CLI verified the same reconstructed signed payload. These are three distinct tool invocation paths, but they MUST NOT be described as three independent machines or three fully independent cryptographic implementations: Python `cryptography` documents that it depends on OpenSSL for cryptographic operations, and Node.js documents that its `crypto` module wraps OpenSSL functions. The exact build linkage used by each local binary was not independently attested here. Therefore this test provides cross-interface agreement, not full cryptographic implementation diversity. The documented basis is [cryptography OpenSSL usage](https://cryptography.io/en/stable/openssl/) and [Node.js crypto documentation](https://nodejs.org/en/docs). These results support the cryptographic relation between the exact preimage and embedded public key, while leaving canonical SSHSIG CLI interoperability and a further independently implemented Ed25519 oracle as additional assurance steps.

**Limitations:** the standard `ssh-keygen -Y verify` command was not available, so this record does not claim that the canonical OpenSSH CLI completed an end-to-end run. Python `cryptography`, the OpenSSL CLI, and Node.js `crypto` are not three independent machines or necessarily three independent cryptographic primitives; at least the former two documented paths use OpenSSL, and Node.js `crypto` is also an OpenSSL wrapper. The exact build linkage was not independently attested. The result demonstrates agreement across tool interfaces, not three-way independent implementation diversity. Complete assurance should add an OpenSSH `ssh-keygen -Y verify` run and, where required, another Ed25519 implementation with independently documented cryptographic backend.

## 5. Time, revocation, and identity are separate questions

1. **Signing time:** SSHSIG's envelope fields do not contain a signing timestamp. The declaration text states `Date: 2026-09-24`. GitHub reports that the commit registering the declaration was authored at `2026-09-24T20:08:08Z` and committed at `2026-09-24T20:09:57Z`, but the GitHub API marked that Git commit signature `verified: false`, reason `unknown_key`. Commit time is not a cryptographically bound signature-creation time.
2. **Revocation:** the reviewed recursive tree and code searches did not surface a key-revocation list or revocation record. `allowed_signers` registers a key; it is not a revocation source. The key's broader revocation status remains **NOT ESTABLISHED**.
3. **Identity:** a correct signature proves that the corresponding private key signed the reconstructed payload. It does not prove, without an independent binding, which natural person controlled the key at signing time.
4. **Authority:** the same key signs the declaration and the Authority Binding record that asserts its constitutive authority. This internal consistency is not an independent source granting that authority.

## 6. Correction to the earlier source-review claim

The existing `governance/evidence/AURA_ARTICLE_XIII_AUTHORSHIP_AND_INTENT_RECORD_v0.1.md` describes the SSHSIG inner signature-algorithm identifier as `sshoed25519`. The exact current repository artefact instead parses as `ssh-ed25519` in both independent parsers, and the mathematical verification passes in Python, OpenSSL, and Node.js. The earlier statement is therefore **not supported by the exact bytes reviewed here** and should be treated as a superseded technical observation.

This correction is narrow. It does not resolve the separate findings about identity, key revocation, signing time, competent source, constitutional amendment procedure, or normative effect.

## 7. Final result

- **Genesis detached-signature cryptographic check:** PASS (exact bytes; independent crypto engines).
- **SSHSIG structure check:** PASS by local parsers; canonical OpenSSH CLI interoperability: NOT RUN.
- **Signature creation time / non-revocation / real-world identity:** NOT ESTABLISHED.
- **Constitutional competence and Article XIII procedural effectiveness:** NOT ESTABLISHED.
- **G1 disposition:** **BLOCKED** pending source-level authority evidence and a reasoned constitutional-procedure disposition.

No authorization is created by this report. It is an audit record draft, not a ratification, appointment, legal opinion, or amendment to the protocol.
