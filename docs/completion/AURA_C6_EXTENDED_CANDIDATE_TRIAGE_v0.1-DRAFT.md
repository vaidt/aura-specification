# C6 Extended Candidate Vector Triage — Draft

Assessment date: 2026-10-25  
Status: DRAFT / NON-NORMATIVE / NOT A CONFORMANCE RESULT  
Baseline: `vaidt/aura-specification@6b4f3dcc46841bb17fafa3e1b1cc8ea9c0397330`, original 27-case manifest (Git blob OID `d9b4a1f488185a44f7edb233ef8ff180981f0e84`).

## Purpose

This branch holds an inventory of 50 candidate C6 expansions. It is separate from the original 27-case corpus and does not replace its manifest or results. Candidate expectations remain unlocked until each vector is bound to a controlling contract clause and error-taxonomy entry.

## First-pass duplicate disposition

| Candidate | Result | Existing case | Basis |
|---|---|---|---|
| C6-X-004 — missing `receiver` object | Exact duplicate; exclude from active pool | C6-N-015A | Original manifest already deletes the top-level `receiver` field and expects MISSING_FIELD. |
| C6-X-009 — unknown property under `received` | Exact duplicate; exclude from active pool | C6-N-012A | Original manifest already inserts an unknown nested property under `received` and expects UNKNOWN_FIELD. |

| `C6-X-041` — zero-filled digest mismatch | **Exact duplicate; exclude from active pool** | `C6-N-006A` | Both set `received.recomputed_sha256` to 64 zeroes over the same source seed; the existing manifest already expects `DIGEST_MISMATCH`. |

Triage accounting: 50 candidates; 2 exact mutation duplicates and 1 semantic coverage duplicate are retained as traceable tombstones; 47 remain in the active candidate pool for byte-level deduplication and contract mapping; 0 are yet approved as runnable contract-bound vectors.

## Candidate inventory groups

| IDs | Count | Coverage area | Current condition |
|---|---:|---|---|
| C6-X-001…012 | 12 | Missing/unknown nested members | 2 exact overlaps found; remaining cases pending review |
| C6-X-013…020 | 8 | JSON top-level shape, BOM, trailing/concatenated content, escaped duplicate keys, non-standard numeric constants | Pending contract binding and raw-byte definition |
| C6-X-021…028 | 8 | Base64 alphabets, whitespace, padding, pad bits, non-ASCII input, line breaks, re-encoding and full-octet round-trip | Partial overlap with existing strict/canonical checks to be assessed |
| C6-X-029…035 | 7 | Numeric types, lexical forms, zero/negative zero and limits | Limits/lexical semantics require a documented contract decision |
| C6-X-036…041 | 6 | SHA-256 representation and digest-input variants | Existing digest-format/mismatch controls overlap at class level; exact variants remain to be checked |
| C6-X-042…046 | 5 | Required identity/provenance values and prohibited result values | Contract rules for source-commit shape and required values must be established |
| C6-X-047…050 | 4 | Error precedence, size/nesting limits and bounded fuzz seeds | Pending contract and limit definitions |

## Entry requirements before executable CI

Each accepted vector must have a stable ID and version; controlling clause/invariant; deterministic mutation recipe; exact materialized input bytes, byte length and SHA-256; a justified acceptance/rejection expectation; and matching source/runtime bindings for RI-PY and RI-RS. Any unresolved expected behavior remains `CONTRACT_DECISION_REQUIRED`.

The first CI task for this branch validates only inventory metadata (50 stable IDs, two documented duplicates, unique IDs, non-normative status fields and absence of locked expected outcomes). It does not execute either parser. A later, separate exploratory lane must materialize and hash exact input bytes, record observations from both implementations, flag unexplained differences, and label results `EXPLORATORY_NON_NORMATIVE`.

## Effects

The original 27-case manifest, prior run artifacts and their digests remain untouched. This inventory does not change `c6_gate_status=BLOCKED_PENDING_EVIDENCE_REVIEW`, CONF-003, DQ-006, M1/G1, or release authorization.
