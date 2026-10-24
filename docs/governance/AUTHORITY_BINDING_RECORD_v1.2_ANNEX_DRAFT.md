# Authority Binding Record v1.2 — Annex Draft: Genesis Evidence Digests

**Artifact ID:** AURA-BIND-ROOT-v1.2-ANNEX-DRAFT  
**Version:** 0.1-DRAFT  
**Status:** PROPOSED · NON-CONSTITUTIVE · NOT RATIFIED  
**Normative effect:** NONE  
**Supersedes:** Nothing  
**Parent record:** `AUTHORITY_BINDING_RECORD_v1.1.md` — cited for traceability only

> This is a proposed evidence-digest annex. It does not amend or supersede Authority Binding v1.1, create identity binding, create authority, ratify Genesis, or authorise any AURA activity.

## 1. Purpose

Record the verified technical relationship between the Genesis declaration and the key described in the current Authority Binding record. The digest record is evidence of byte identity and cryptographic verification only. A digest is not a source of authority.

## 2. Frozen references

Observed repository baseline: `vaidt/aura-specification@8f0cd6be94a68a3728e69a1d21d49237c9d8bd05`.

| Artefact | Git blob SHA-1 | SHA-256 of file bytes |
|---|---|---|
| `GENESIS_DECLARATION.txt` | `9c19e97270a4539ea7788a0553db2a800a573c44` | `6b5a4c4eaa258eef27452fe6a2f2d752484ae6c88968a039b0b40ca0ac8f2bb6` |
| `GENESIS_DECLARATION.txt.sig` | `82f114a695c5b30094500452c8770cb4d6d572f5` | `154f34a66e57cf5a9af1e83a6747fd925cf3f5b2a8e0bc7291eebf2e4b3acb15` |
| `AUTHORITY_BINDING_RECORD_v1.1.md` | `f9dbbcc138a2e0d1bdb34aea2a238394a28ed2cd` | `9544bee7bb3a042cac5041deb73706832c04c5d0e83f5c01252c71e839e678f0` |
| `AUTHORITY_BINDING_RECORD_v1.1.md.sig` | `eed7842fc54f5bfeaaafecca63f5dfbe24823b79` | `2c7968dbdfe3153a24f0aeb2316e922f3c8e8bf4d106c8710863b1fcd8598c67` |
| `allowed_signers` | `fa4fa29ed870f350f38157e9a1e15fe9654a6f86` | — |

## 3. Cryptographic relationship

- Genesis namespace: `aura-genesis`.
- Authority Binding namespace: `aura-governance`.
- Algorithm: Ed25519, encoded as `ssh-ed25519`.
- Hash algorithm in both SSHSIG envelopes: `sha512`.
- Fingerprint calculated from the complete SSH public-key blob: `SHA256:u9HaNYWZGQYvGET5ZaX2c/V56MzL0Xo7Ilg9M1pZRwU`.
- Both exact preimages verified in Python `cryptography`, OpenSSL 3.5.5, and Node.js v22.16.0.
- The standard `ssh-keygen -Y verify` command was not run because OpenSSH was unavailable in the audit environment.

**Technical evidence disposition:** Cryptographic relation between the two artifacts and the same key — **PASS**. Canonical OpenSSH CLI interoperability — **NOT RUN**.

## 4. Explicitly excluded implications

The above facts do not, by themselves, establish any of the following:
- independent proof of the natural-person identity of the key holder;
- proof that the key holder was authorised to create Genesis Authority;
- proof of an exclusive legal right to convert repository ownership into constitutional authority;
- proof that Article XIII was properly adopted under Article XI;
- proof of the date or time the detached signature was created;
- proof that the key is not revoked;
- any present competence to ratify `AURA-STAGE3-AUTH-001`.

## 5. Preconditions for any future normative v1.2

This draft must not be promoted to an effective v1.2 record until a competent issuer has been independently established for the act and the authority gaps in [the Article XIII audit opinion](ARTICLE_XIII_CONSTITUTIONAL_AUDIT_OPINION.md) have been resolved. The eventual act must define the authority basis, exact approved bytes/digest, signing and verification procedures, registration location, effective date, scope, and any supersession terms.

Until then:
- Authority Binding v1.1 remains the repository's indexed record of reference, subject to the source-level conflicts explicitly recorded by the audit.
- This annex remains **PROPOSED / NON-CONSTITUTIVE / NOT RATIFIED**.
- No authority or implementation permission is created.
