# Stage C — JCS Multi-Vector Expansion C4 (Draft)

**State:** DRAFT · NON-NORMATIVE · NOT RATIFIED  
**Branch:** `experiment/stage-c-jcs-multivector-20261023`  
**Baseline:** CANONICAL-003 single-vector evidence retained unchanged  
**Authority / governance / release effect:** NONE

## Purpose

Extend the existing single-vector byte comparison with a bounded corpus that exercises additional RFC 8785 behaviors using the same external adapter request/response contract. The new workflow runs the Python JCS shim and the separately pinned Rust JCS shim as independent processes. The previously successful RI-PY production-path comparison remains a separate, single-vector result.

## Corpus

| Vector | Primary coverage |
|---|---|
| JCS-VECTOR-001 | RFC 8785 primitive example: number rendering, literals, escaping |
| JCS-VECTOR-002 | Recursive key sorting and UTF-16 order for U+10000 versus U+E000 |
| JCS-VECTOR-003 | Control-character escaping, quotes, backslash, U+2028/U+2029 and Unicode |
| JCS-VECTOR-004 | Nested objects, objects inside arrays, array-order preservation and empty containers |
| JCS-VECTOR-005 | RFC 8785 Appendix B number-rendering boundaries, including subnormal and maximum finite values |
| CANONICAL-003 | Frozen original discriminator and regression baseline |

Each vector has a committed input, expected canonical octets, SHA-256 digest, output length, and manifest entry. Expected outputs must match in raw bytes; semantic JSON equality is insufficient.

## Execution and acceptance criteria

C4 is an engineering comparison only. It passes only if all six vectors satisfy all of the following:

1. Manifest input and expected-output digests match the committed files.
2. Both adapters accept the same fixture ID, request operation, input path and JSON Pointer.
3. Both output byte sequences equal the committed expected octets exactly and equal each other.
4. Independent output SHA-256 and byte length match the manifest.
5. Response envelopes bind to the exact input bytes, run ID, adapter language and pinned source revision.
6. No output includes an appended line feed.

A divergence or missing provenance field is a failure; it must not be waived or re-labeled as PASS. The runner uploads per-vector requests, responses, raw bytes, command logs and a summary report for inspection.

## Explicit limits

- This is a bounded corpus, not complete RFC 8785 certification.
- The new multi-vector workflow executes isolated Python/Rust JCS adapters. It does **not** establish that every new vector traverses the RI-PY or RI-RS production path.
- The previous four-output equality for CANONICAL-003 is retained as evidence for that exact vector and source pin; it is not expanded by implication.
- No Merkle internal-node domain rules, proof shape/verification, chain behavior, or protocol-specific negative tests are tested by C4.
- The existing `cargo-audit` and `cargo-deny` failures are not modified or suppressed.
- No DQ-006/DQ-002 status, CONF-003 disposition, governance state, authority state, release state, or protected branch is changed.

## Next gate

After C4 evidence is reviewed and all six vectors pass, prepare C5 independently for Merkle leaf/node domain separation, tree shape, proof construction and verification. C6 protocol-specific negative tests follow C5. Neither gate is authorized by this draft itself.
