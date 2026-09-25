# AURA — Commit 02 / Structural Extraction
## Path Relocation Matrix v1.0 — DRY-RUN / NON-EXECUTING

**Repository:** `vaidt/aura-specification`  
**Current branch:** `work/protocol-core-extraction-v1`  
**Current HEAD:** `fec5991cbca601a89f7c3eeee1927ad6a3236568`  
**Reference base:** `main @ a16b9001377135467a5e315862db19ce9adb47ed`  
**Proposed target root:** `protocol-core/`  
**Execution mode:** review only; NO `git mv` performed

> This matrix defines proposed relocation topology only. It is not a normative decision and does not authorize physical movement by itself.

## 0. Procedural control note

The previously prepared extraction plan defined **Commit 02** as `Canonical Core Index` and **Commit 05** as `Structural Extraction`. The independent review supplied for `AURA-REV-EXT-B1-v1.0` refers to the structural extraction gate as **Commit 02**.

This matrix therefore treats the present item as the **pre-execution relocation control for the structural-extraction gate**. No attempt is made here to silently reconcile those two labels.

## 1. Relocation matrix

| ID | Current path | Proposed target | Mode | Dependency / control | Pre-execution status |
|---|---|---|---|---|---|
| RM-001 | `constitution/AURA_CONSTITUTION.md` | `protocol-core/constitution/AURA_CONSTITUTION.md` | MOVE + coupled legacy source | Relative source link requires `AURA Constitution_260723_190157.txt` to move to `protocol-core/` or a separately approved link rebase | HOLD |
| RM-002 | `aps/APS-000_FOUNDATION_AND_TERMINOLOGY.md` | `protocol-core/aps/APS-000_FOUNDATION_AND_TERMINOLOGY.md` | MOVE + coupled deps | Links `../invariants/INVARIANT_REGISTRY.md` and root historical `.txt` companion | HOLD until dependency closure |
| RM-003 | `specification/APS-001_PROTOCOL_SPECIFICATION.md` | `protocol-core/specification/APS-001_PROTOCOL_SPECIFICATION.md` | PURE MOVE | No relative refs detected in source scan | READY-DRY-RUN |
| RM-004 | `aps/APS-100_PROTOCOL_INVARIANTS.md` | `protocol-core/aps/APS-100_PROTOCOL_INVARIANTS.md` | MOVE + coupled deps | Depends on `invariants/`, `compliance/TRACEABILITY_MATRIX.md`, root historical `.txt` | HOLD |
| RM-005 | `aps/APS-200_CANONICAL_DATA_MODEL.md` | `protocol-core/aps/APS-200_CANONICAL_DATA_MODEL.md` | PURE MOVE | No relative refs detected in source scan | READY-DRY-RUN |
| RM-006 | `aps/APS-300_EVIDENCE_MODEL.md` | `protocol-core/aps/APS-300_EVIDENCE_MODEL.md` | MOVE + coupled legacy source | Root historical `.txt` companion | HOLD until companion handling fixed |
| RM-007 | `aps/APS-400_CONFORMANCE_TEST_MATRIX.md` | `protocol-core/aps/APS-400_CONFORMANCE_TEST_MATRIX.md` | MOVE + large dependency closure | Links `conformance/`, `compliance/`, `templates/`, root historical `.txt` | HOLD |
| RM-008 | `aps/APS-500_REFERENCE_FIXTURES.md` | `protocol-core/aps/APS-500_REFERENCE_FIXTURES.md` | MOVE + coupled fixtures/source | Links `fixtures/` and root historical `.txt`; fixture subtree must be checked as a closure | HOLD until fixture closure recorded |
| RM-009 | `aps/APS-900_COMPLIANCE_MAPPING.md` | `protocol-core/aps/APS-900_COMPLIANCE_MAPPING.md` | MOVE + governance deps | Links `compliance/`, `templates/`, root historical `.txt` | HOLD |
| RM-010 | `aps/APS-950_REFERENCE_IMPLEMENTATION_REQUIREMENTS.md` | `protocol-core/aps/APS-950_REFERENCE_IMPLEMENTATION_REQUIREMENTS.md` | MOVE + coupled legacy source | Root historical `.txt` companion | HOLD until companion handling fixed |
| RM-011 | `aps/EVENT_TYPE_REGISTRY.md` | `protocol-core/aps/EVENT_TYPE_REGISTRY.md` | PURE MOVE | No relative refs detected in source scan | READY-DRY-RUN |
| RM-012 | `invariants/INVARIANT_REGISTRY.md` | `protocol-core/invariants/INVARIANT_REGISTRY.md` | MOVE | No relative refs detected; required by APS-000 / APS-100 after move | READY-DRY-RUN with coupled-doc verification |
| RM-013 | `fixtures/README.md` | `protocol-core/fixtures/README.md` | MOVE + external deps | Links `../ROADMAP.md` and `../templates/FIXTURE_TEMPLATE.json` | HOLD |
| RM-014 | `conformance/README.md` | `protocol-core/conformance/README.md` | MOVE + external dep | Links `../templates/CONFORMANCE_TEST_TEMPLATE.md` | HOLD |
| RM-015 | `reference/RI-PY_AURA_POC_A_CORE.md` | `protocol-core/reference/RI-PY_AURA_POC_A_CORE.md` | PURE MOVE | No relative refs detected in source scan | READY-DRY-RUN |
| RM-016 | `reference/RI-RS_AURA_GUARD.md` | `protocol-core/reference/RI-RS_AURA_GUARD.md` | PURE MOVE | No relative refs detected in source scan | READY-DRY-RUN |

## 2. Dependency closure records

### 2.1 Historical companion files

These files are referenced by relative links from candidate core documents and are therefore part of the relocation-control graph:

- `AURA Constitution_260723_190157.txt`
- `AURA Protocol Specification APS-000 — Foundation &_260723_191759.txt`
- `APS-100 — Protocol Invariants_260723_192315.txt`
- `APS-300 — Evidence Model_260723_193234.txt`
- `APS-400 — Conformance Test Matrix_260723_193617.txt`
- `APS-500 Reference Fixtures_260723_194023.txt`
- `APS-900 — Compliance Mapping_260723_194128.txt`
- `APS-950 — Reference Implementation Requirements_260723_194507.txt`

**Control:** do not move a referencing document without either moving its historical companion into the equivalent relative location or obtaining an explicitly reviewed link-rebase change.

### 2.2 Cross-subtree dependencies

| Dependency | Referencing source | Control |
|---|---|---|
| `invariants/INVARIANT_REGISTRY.md` | APS-000, APS-100 | Can move as coupled subtree |
| `compliance/TRACEABILITY_MATRIX.md` | APS-100, APS-400, APS-900 | Do not move until compliance layer classification is reviewed |
| `conformance/` + selected CONF files | APS-400 | Do not move until conformance closure dependencies are reviewed |
| `templates/CONFORMANCE_REPORT_TEMPLATE.md` | APS-400, APS-900 | Keep outside core unless separately classified |
| `templates/FIXTURE_TEMPLATE.json` | `fixtures/README.md` | Keep outside core unless separately classified |
| `templates/CONFORMANCE_TEST_TEMPLATE.md` | `conformance/README.md` | Keep outside core unless separately classified |
| `ROADMAP.md` | `fixtures/README.md` | Keep outside core; README relocation should remain HOLD |
| `closures/DQ-006_CLOSURE_PACKAGE.md` | `conformance/CONF-003_CANONICAL_SERIALIZATION.md` | Conformance relocation must not break this path |

## 3. Fixture/schema relative-reference control

The inspected schema files showed:

- `fixtures/schemas/event_types.json` contains only an internal JSON Schema `$ref` (`#/$defs/eventType`);
- `fixtures/schemas/common-object-contract.schema.json` contains no `$ref` in the inspected payload;
- `event_types.json` contains a `$id` URL containing the historical repository path.

**Rule:** do not rewrite `$ref`, `$id`, schema identifiers, or fixture semantics during structural extraction. A path-like `$id` is not automatically a relative filesystem reference and must not be normalized silently.

## 4. Commit 02 execution preconditions

Before any physical move:

1. Freeze the relocation matrix as the reviewed target topology.
2. Produce a complete dependency closure for every `MOVE` item.
3. Confirm target paths are collision-free.
4. Record source Git blob SHA-1 and SHA-256 for every file scheduled to move.
5. Perform dry-run reference resolution against the proposed post-move tree.
6. Execute only approved moves with `git mv`.
7. Recompute SHA-256 after relocation and require byte-for-byte equality.
8. Verify internal links and `$ref`/`$id` behavior.
9. Verify no protected protocol content changed.
10. Compare source and post-move content to prove structural-only change.

## 5. Hard prohibitions

- No semantic edit to protocol text.
- No identifier changes.
- No fixture payload edits.
- No silent link rewriting.
- No deletion of historical evidence.
- No governance-state reconciliation.
- No change to implementation authorization.
- No merge to `main`.
- No force-push.
- No Commit 03/05+ work before this gate is independently reviewed.

## 6. Current dry-run disposition

**Physically executable now, subject to this matrix being accepted:** RM-003, RM-005, RM-011, RM-012, RM-015, RM-016.

**Must remain HOLD pending dependency closure:** RM-001, RM-002, RM-004, RM-006, RM-007, RM-008, RM-009, RM-010, RM-013, RM-014.

**No physical extraction has been performed by this artifact.**