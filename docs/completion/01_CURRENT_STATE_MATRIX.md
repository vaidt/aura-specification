# Aura Specification — Current-State Conformance Matrix

**Baseline:** `main` @ `62d2d6bcc1a46dd505ebfe400ad01fa3c6a25bf0`  
**Assessment branch:** `completion/aura-specification-conformance`  
**Assessment rule:** existence of a document is not evidence of conformance.

| Domain | Current state | Evidence | Closure requirement |
|---|---|---|---|
| Constitution | **FROZEN / PASS** | `constitution/AURA_CONSTITUTION.md` | No content change; amendments only through constitutional process |
| APS-000 | **DRAFT** | `aps/APS-000_FOUNDATION_AND_TERMINOLOGY.md` | Complete review + approval |
| APS-001 | **DRAFT / CRITICAL** | `specification/APS-001_PROTOCOL_SPECIFICATION.md` exists as `0.2-DRAFT — ARCHITECTURE REVIEW REQUIRED` | Reconcile dependent APS documents + complete Architecture Review / approval path |
| APS-100 | **DRAFT / OPEN** | 15 invariants defined and mapped to CONF-001…015 | Align authority, verification language and execution evidence with APS-001 |
| APS-200 | **DRAFT / OPEN** | Canonical entities + common object contract; draft machine-readable schemas now close the current working-profile ENT-002/ENT-003 payloads under `fixtures/schemas/` | Additional profile schemas, identity closure, approved event-type registry tokens, compatibility matrix |
| APS-300 | **DRAFT / OPEN** | Evidence model exists; draft machine-readable Evidence Object / Evidence Pack schemas now publish a concrete current draft `EPR-CORE` content contract for `FIX-001` under `fixtures/schemas/` | Attestation lifecycle closure beyond the current draft working path, additional profile vocabularies, executable fixture/evidence path |
| APS-400 | **DRAFT / INCOMPLETE** | CONF-001…015 documents exist; CONF-001/004/005/010 now have a repository-local draft execution path via `scripts/check-fix001-evidence.py` | Execute the matrix through a runner and gather objective PASS/FAIL evidence |
| APS-500 | **DRAFT / INCOMPLETE** | Fixture contract exists; `FIX-001` now supports a repository-local draft request/result/evidence gate for CONF-001/004/005/010 | Publish canonical machine-readable fixture set and expected outputs |
| APS-900 | **DRAFT / INCOMPLETE** | Traceability model exists | Every normative requirement must resolve to test, fixture, evidence, implementation and release |
| APS-950 | **DRAFT / OPEN** | RI requirements exist | Reference implementation certification after conformance gate |
| Invariant Registry | **DRAFT / OPEN** | `INVARIANT_REGISTRY.md` maps all invariants to CONF identifiers | Validate assignments against executable evidence and finalized normative contracts |
| Traceability Matrix | **DRAFT / INCOMPLETE** | `compliance/TRACEABILITY_MATRIX.md` contains current mappings but mixed status maturity | Populate objective statuses; no unsupported PASS claims |
| CK-003 DQ-002 | **PARTIAL / EVIDENCE PRESENT** | `ck003/dq-002-hash-domain` | Keep only the accepted hash-domain contract as normative and preserve the rest as evidence/history |
| CK-003 DQ-003 | **OPEN / SNAPSHOT ONLY** | versioning snapshot and decision material exist, but closure is not yet evidenced end-to-end | Record normative version semantics, fixture binding and promotion status explicitly |
| CK-003 DQ-004 | **OPEN** | No DQ-004 closure package on `main` found | Complete event-type semantics, fixture, conformance and gate |
| CI | **OPEN / CRITICAL** | `.github` contains CODEOWNERS/templates but no workflow directory on `main` | Add executable repository-native conformance CI |
| Release v1.0 | **NOT READY** | Roadmap Milestone 4 remains unchecked | Only release after all mandatory gates are evidenced |

## Immediate blockers

1. **APS-001** is the root normative blocker.
2. **INV-010** is mapped structurally, but CONF-011…CONF-015 still require executable evidence before they can support PASS claims.
3. APS-200/300 now expose draft machine-readable schemas, but APS-300 remains incomplete beyond the current draft `EPR-CORE` working path and APS-200 still needs additional profile contracts.
4. APS-500 does not yet provide the complete canonical fixture corpus required by APS-400/950.
5. The repository lacks an executable GitHub Actions conformance gate.
6. CK-003 evidence exists, but unresolved DQ-003/DQ-004 and release-gate promotion still block closure.

## Execution order

`APS-001 → normative reconciliation → DQ closure → APS-200/300 schemas → complete INV/CONF matrix → fixtures → executable runner → CI → RI-PY/RI-RS certification → release evidence`.

## Immediate backlog — NOW

| Work package | Status | Immediate output |
|---|---|---|
| WP-1 APS-001 gap list | CLOSED | Per-section `READY FOR REVIEW / OPEN / BLOCKED` list for APS-001 recorded in `docs/completion/00_MASTER_COMPLETION_PLAN.md` |
| WP-2 APS reconciliation | OPEN | Initial reconciliation recorded for APS-100 / APS-200 / APS-300 and second-wave corrections recorded for APS-400 / APS-500 / APS-900 |
| WP-3 CK-003 blocker register | CLOSED | CK-003 register recorded with explicit states for DQ-002 / DQ-003 / DQ-004 / DQ-006 and a minimal active DQ set |
| WP-4 Traceability gap pass | CLOSED | One explicit `OPEN / BLOCKED / READY / NOT VERIFIED` state recorded for each invariant in the completion plan |
| WP-5 Fixture promotion plan | CLOSED | Fixture promotion register and minimum early conformance fixture set recorded in the completion plan |
| WP-6 Minimum automation plan | CLOSED | Phased automation order, immediate script scope, and deferred schema-bound tooling recorded in the completion plan |
