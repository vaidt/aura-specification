# AURA — COMMIT 03: DEPENDENCY CLOSURE RECORD v1.0

Domain: Structural Extraction Dependency Analysis & Topology Closure
Repository: vaidt/aura-specification
Branch: work/protocol-core-extraction-v1
Baseline_HEAD: 1e0a9b9199be41953fb29f7a2051eb667d9579c9

Status: TECHNICAL_CLOSURE_ANALYSIS_RECORDED
Physical_Execution: BLOCKED

## 1. Purpose

This record documents the dependency-closure analysis performed before any physical structural extraction.

No git mv operation is authorized by this record.

No protocol semantic change, identifier change, fixture payload change, governance-state change, or implementation-authorization change is included.

## 2. Node 1 — Historical Text Companions

Eight historical .txt companions referenced by candidate core Markdown documents were verified as physically present in the repository working tree.

The following SHA-256 digests were computed from the exact local file bytes:

| File | Size | SHA-256 | Status |
|---|---:|---|---|
| AURA Constitution_260723_190157.txt | 4285 | 1713a97c90d8c3886323322b94977e9c41fa018cf5d68276cf9399cf43bccd6b | VERIFIED |
| AURA Protocol Specification APS-000 — Foundation &_260723_191759.txt | 4887 | 8cf9ab0ba23976d32a9d3dc93eb7360caff8b12b457816335b77b11c69ceb8a6 | VERIFIED |
| APS-100 — Protocol Invariants_260723_192315.txt | 4636 | a22075cf0ab217adbf5fb72ed866be41162ff8b1d44f41617bbcb9002469cbd7 | VERIFIED |
| APS-300 — Evidence Model_260723_193234.txt | 3928 | c7f17709ac21827a4b8c96e44595e033f5e473175fc40372643887aaa123544a | VERIFIED |
| APS-400 — Conformance Test Matrix_260723_193617.txt | 3862 | d03742b397f6c11ea86b91a945d007dd9d76497a60494192e6105a2bf81fca92 | VERIFIED |
| APS-500 Reference Fixtures_260723_194023.txt | 2567 | 057d7bb0bb7d5db8bdcd17e02c4e393b0e982a298ba0afec1a3c46415fc3ab34 | VERIFIED |
| APS-900 — Compliance Mapping_260723_194128.txt | 3274 | 03d240a8de2ff21f57248fc986f29a2a148798db2f0aa9a0772d4d377254d35d | VERIFIED |
| APS-950 — Reference Implementation Requirements_260723_194507.txt | 3346 | 35ece8c7e36c1b8e9bdbd6f68e9f7fecd215a868b42e758df16482f10d948a70 | VERIFIED |

Determination: CLOSED & VERIFIED.

Rule: Markdown documents and their historical .txt companions remain atomic relocation pairs unless a separately reviewed topology decision establishes another arrangement.

## 3. Node 2A — Invariants Topology

The following relative references were verified:

- aps/APS-000_FOUNDATION_AND_TERMINOLOGY.md -> ../invariants/INVARIANT_REGISTRY.md
- aps/APS-100_PROTOCOL_INVARIANTS.md -> ../invariants/INVARIANT_REGISTRY.md

A symmetrical relocation of:

- protocol-core/aps/
- protocol-core/invariants/

preserves the literal relative reference ../invariants/INVARIANT_REGISTRY.md without changing source-file bytes.

Determination: CLOSED & VERIFIED — TOPOLOGY PRESERVED.

## 4. Node 2B — Boundary Topology

The following cross-subtree dependencies were verified:

APS-100:
- ../compliance/TRACEABILITY_MATRIX.md

APS-400:
- ../conformance/
- ../conformance/CONF-011_ZERO_FLOAT_RUNTIME.md
- ../conformance/CONF-012_AUDITABILITY.md
- ../conformance/CONF-013_POLICY_DETERMINISM.md
- ../conformance/CONF-014_REFERENCE_COMPATIBILITY.md
- ../conformance/CONF-015_CANONICAL_IDENTITY.md
- ../templates/CONFORMANCE_REPORT_TEMPLATE.md
- ../compliance/TRACEABILITY_MATRIX.md

APS-500:
- ../fixtures/FIX-001_BASIC_EVALUATION.json
- ../fixtures/

APS-900:
- ../compliance/TRACEABILITY_MATRIX.md
- ../templates/CONFORMANCE_REPORT_TEMPLATE.md

CONF-003:
- ../fixtures/corpus/CANONICAL-001_jcs_evidence.json
- ../closures/DQ-006_CLOSURE_PACKAGE.md

Under Content Diff = NONE, these references cannot be rewritten merely to adapt to a new protocol-core root.

Therefore relocation of affected files while their referenced external subtrees remain outside protocol-core would create a path-topology conflict.

Determination: OPEN / HOLD — BOUNDARY TOPOLOGY UNRESOLVED.

No physical move is authorized for Node 2B.

## 5. Node 3 — Fixtures and Schemas

The following object exists:

fixtures/core/FIX-001_BASIC_EVALUATION.json

The following relative reference exists in APS-500:

../fixtures/FIX-001_BASIC_EVALUATION.json

The exact referenced path is missing.

Independent filesystem inspection confirmed:

MISSING fixtures/FIX-001_BASIC_EVALUATION.json
PRESENT fixtures/core/FIX-001_BASIC_EVALUATION.json

Classification:

BASELINE PRE-EXISTING BROKEN REFERENCE

This condition predates the structural extraction procedure and must not be silently corrected during extraction.

Additional inspected fixture dependencies:

- fixtures/corpus/CANONICAL-001_jcs_evidence.json is present.
- fixtures/schemas/ and fixtures/corpus/ do not establish a basis for rewriting schema or fixture semantics during structural extraction.
- fixtures/README.md has external documentation dependencies including ../ROADMAP.md and ../templates/FIXTURE_TEMPLATE.json.

Determination: TECHNICALLY VERIFIED WITH PRE-EXISTING DEFECT RECORDED.

## 6. Dependency Closure Summary

| Node | Scope | Determination | Physical Move |
|---|---|---|---|
| Node 1 | 8 historical .txt companions | CLOSED & VERIFIED | Eligible only as atomic companions |
| Node 2A | APS-000 / APS-100 <-> invariants | CLOSED & VERIFIED | Eligible by symmetrical topology |
| Node 2B | APS-100 / APS-400 / APS-500 / APS-900 / CONF-003 boundary | OPEN / HOLD | PROHIBITED |
| Node 3 | Fixtures, schemas, APS-500 reference | VERIFIED WITH PRE-EXISTING DEFECT | No move until boundary closure is separately resolved |

## 7. Structural Extraction Constraints

Before any physical extraction:

1. Preserve exact source bytes.
2. Preserve Git history where technically possible.
3. Do not rewrite relative links silently.
4. Do not alter $ref, $id, schema identifiers, or fixture semantics.
5. Do not correct pre-existing broken references as part of structural movement.
6. Do not delete historical evidence.
7. Do not modify main.
8. Do not change implementation authorization.
9. Do not promote unresolved governance records.
10. Require a separate pre-execution collision and reference-resolution review.

## 8. Current Gate State

Dependency closure is sufficient for recording the verified topology findings above.

It is NOT sufficient to authorize physical extraction.

Current gate state:

PHYSICAL EXTRACTION: BLOCKED
NODE 2B: OPEN / HOLD

This record is technical evidence and structural control documentation only.

It does not constitute normative ratification, governance closure, implementation authorization, or a decision to move files.
