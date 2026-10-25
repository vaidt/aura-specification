# C6 Candidate Triage — Correction Addendum

**Date:** 2026-10-25  
**Status:** DRAFT / NON-NORMATIVE  
**Applies to:** `AURA_C6_EXTENDED_CANDIDATE_TRIAGE_v0.1-DRAFT.md` and `STAGE-C-C6-EXTENDED-CANDIDATE-INVENTORY-v0.1-DRAFT.json`

## Corrected first-pass accounting

The inventory contains 50 candidate entries. Three are currently excluded from the active triage pool:

| Candidate | Baseline reference | Disposition |
|---|---|---|
| `C6-X-004` | `C6-N-015A` | Exact mutation duplicate: both remove the top-level `receiver` object. |
| `C6-X-009` | `C6-N-012A` | Same coverage class, not identical input bytes: both exercise an unknown nested property under `received`, but the key/value differ. |
| `C6-X-041` | `C6-N-006A` | Exact mutation duplicate: both set the digest field to 64 zeroes and expect the already-defined `DIGEST_MISMATCH` class. |

Accounting: **50 total entries; 2 exact mutation duplicates; 1 semantic coverage duplicate; 47 active candidate entries; 0 contract-bound runnable cases.**

The candidate inventory is the machine-checked source for this accounting. Some earlier wording in the original triage document calls `C6-X-009` an “exact duplicate” and describes only two overlaps in its group summary. This addendum corrects that interpretation: `C6-X-009` is a semantic coverage duplicate, not a claim of byte-identical input.

## Limitations

This is a metadata/deduplication pass, not exhaustive byte-level deduplication of every remaining candidate. The remaining 47 entries still require detailed comparison, contract mapping, and exact input materialization before they can be treated as executable test vectors. No expected result is locked by this addendum.

The original 27-case C6 manifest and the artifacts from run `40176350679` are unchanged. All C6 gate, CONF-003, DQ-006, M1/G1 and release statuses remain unchanged.
