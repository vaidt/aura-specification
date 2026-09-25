# AURA — Protocol Core Extraction Baseline v1.0

## 1. Control status

| Field | Value |
|---|---|
| Repository | `vaidt/aura-specification` |
| Source branch | `main` |
| Source commit | `a16b9001377135467a5e315862db19ce9adb47ed` |
| Extraction branch | `work/protocol-core-extraction-v1` |
| Commit scope | **Commit 01 — Baseline Manifest** |
| Baseline date | `2026-09-25` |
| Source files moved | **No** |
| Source files modified | **No** |
| Main branch modified | **No** |
| Normative ratification implied | **No** |
| Implementation authorization changed | **No** |
| Current manifest state | `BASELINE_CAPTURED_SHA256_PENDING` |

## 2. Purpose

This commit establishes an additive, branch-local baseline for the proposed Protocol Core extraction. It records the source point, candidate core surface, initial classifications, known conflicts, and unresolved decisions.

This document is an engineering and audit aid. It is not a ratification instrument, does not establish authority continuity, and does not promote any record to `EFFECTIVE`, `RATIFIED`, or `PROVEN`.

## 3. Controls applied

- `main` was not modified.
- No source file was moved, renamed, deleted, or semantically edited.
- Historical and superseded evidence remains untouched.
- Governance conflicts are recorded as unresolved rather than silently reconciled.
- `PROPOSED`, `PENDING`, `BLOCKED`, and `NOT PROVEN` states are not promoted.
- Git blob SHAs are retained as provenance identifiers; they are not represented as SHA-256 file digests.
- Exact SHA-256 values remain pending deterministic retrieval of the corresponding file bytes.

## 4. Initial candidate Protocol Core surface

The initial candidate surface includes:

- Constitution: `constitution/AURA_CONSTITUTION.md`
- Foundation and terminology: `aps/APS-000_FOUNDATION_AND_TERMINOLOGY.md`
- Protocol specification: `specification/APS-001_PROTOCOL_SPECIFICATION.md`
- Invariants: `aps/APS-100_PROTOCOL_INVARIANTS.md`, `invariants/INVARIANT_REGISTRY.md`
- Canonical data model: `aps/APS-200_CANONICAL_DATA_MODEL.md`
- Evidence model: `aps/APS-300_EVIDENCE_MODEL.md`
- Conformance: `aps/APS-400_CONFORMANCE_TEST_MATRIX.md`, `conformance/`
- Reference fixtures: `aps/APS-500_REFERENCE_FIXTURES.md`, `fixtures/`
- Compliance mapping: `aps/APS-900_COMPLIANCE_MAPPING.md`
- Reference implementation requirements: `aps/APS-950_REFERENCE_IMPLEMENTATION_REQUIREMENTS.md`
- Event vocabulary: `aps/EVENT_TYPE_REGISTRY.md`
- Reference implementations: `reference/RI-PY_AURA_POC_A_CORE.md`, `reference/RI-RS_AURA_GUARD.md`

The list is a **candidate inventory**, not a final canonical index. Classification and dependency validation remain subject to later review.

## 5. Known unresolved conflicts

| ID | Subject | Disposition | Extraction effect | Normative-release effect |
|---|---|---|---|---|
| C-001 | M1 closure state | Unresolved | Review required | Blocking until authority continuity is established |
| C-002 | P-008 ratification/effectiveness state | Unresolved | Review required | Blocking |
| C-003 | DQ-006 historical/current closure state | Unresolved | Review required | Potentially blocking |
| C-004 | Event-type vocabulary and fixture compatibility | Unresolved | Technical reconciliation required | Potentially blocking |
| C-005 | Traceability matrix freshness | Unresolved | Inventory validation required | Potentially blocking |
| C-006 | Implementation authorization | Unresolved | No authorization inferred | Blocking for authorized migration |
| C-007 | Protocol version assignment | Unresolved | Deferred | Blocking for protocol release |

## 6. Unresolved decisions and assumptions prohibited

The following are explicitly not decided by this commit:

1. Which authority chain currently possesses competence to ratify the normative contract.
2. Whether historical closure records retain current normative effect.
3. Whether P-008 is ratified, effective, or authorized for implementation.
4. Whether DQ-006 closure artifacts are current, superseded, or merely historical evidence.
5. Whether event-type registry vocabulary is compatible with all fixtures and receivers.
6. Whether existing traceability matrices are current enough to serve as authoritative indexes.
7. Whether any implementation migration or protocol version assignment is authorized.

## 7. Acceptance status

| Criterion | Status |
|---|---|
| Explicit source commit | **PASS** |
| Dedicated extraction branch | **PASS** |
| No source movement in Commit 01 | **PASS** |
| No `main` mutation | **PASS** |
| Known conflicts recorded | **PASS — initial register** |
| Machine-readable manifest added | **PASS** |
| Human-readable baseline added | **PASS** |
| Complete deterministic SHA-256 inventory | **PENDING** |
| Independent review | **PENDING** |
| Commit 01 fully closed | **BLOCKED pending SHA-256 completion and review** |

## 8. Next controlled step

Before proceeding to Commit 02, complete deterministic SHA-256 calculation for the declared inventory, validate that no candidate source files were silently omitted, and obtain independent review of the baseline classification. No structural extraction should occur until that review is complete.
