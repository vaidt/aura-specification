# Aura Specification — Master Completion Plan

**Status:** EXECUTION DRAFT  
**Branch:** `completion/aura-specification-conformance`  
**Baseline:** `main` @ `62d2d6bcc1a46dd505ebfe400ad01fa3c6a25bf0`  
**Purpose:** Complete the specification repository without silently converting implementation behaviour into normative requirements.

## 1. Governing rule

The AURA Constitution v1.0 is FROZEN. It explicitly establishes **Specification First**, **Explicit over Implicit**, **Version Everything**, and requires conformance against APS-001 and APS-100. AI systems may analyse, propose, implement, and prepare tests, but must not approve or modify frozen canonical documents.

Accordingly, this branch is an implementation workspace. It may contain drafts, evidence, fixtures, conformance tooling, and proposed normative text. No canonical document is treated as approved merely because it exists on this branch.

## 2. Verified starting condition

- `specification/APS-001_PROTOCOL_SPECIFICATION.md` is currently `0.2-DRAFT`, `Status: DRAFT — ARCHITECTURE REVIEW REQUIRED`. It now exists as the root normative draft, but remains the principal repository-level blocker until review and approval.
- APS-100 through APS-500, APS-900 and APS-950 exist as `1.0-DRAFT` documents.
- APS-100 defines 15 invariants and requires every invariant to have a conformance test and evidence path.
- APS-400 defines CONF-001 through CONF-015, but the repository currently contains draft test-definition documents rather than an end-to-end executable conformance gate.
- APS-500 defines the reference-fixture contract, but the canonical fixture set is not yet demonstrably complete against the invariant/test matrix.
- APS-900 defines the required traceability chain from Constitution → APS Requirement → Invariant → Data Model → Evidence → Conformance Test → Fixture → Implementation → Release.
- APS-950 identifies RI-PY (`aura-poc-a-core`) and RI-RS (`aura-guard`) as reference implementations and requires a full conformance process.
- The repository currently has no `.github/workflows/` directory in the default branch; therefore a repository-native CI conformance gate is not yet evidenced.
- CK-003 closure material exists in-repository, but evidence presence is not equivalent to normative closure; DQ-003/DQ-004 and release-gate promotion still require explicit review and acceptance.

## 3. Completion gates

### G0 — Baseline and repository hygiene

Freeze the current main SHA, inventory branches, identify unmerged CK-003 evidence, and establish one completion branch.

### G1 — Root normative specification

Draft APS-001 from first principles using the Constitution and existing APS documents as constraints. Resolve scope, execution lifecycle, inputs, outputs, policy semantics, evidence generation, cryptographic domains, errors, conformance, and normative references.

### G2 — Normative consistency

Reconcile APS-100/200/300/400/500/900/950 against APS-001. Every MUST-level requirement must have a traceability path and no document may introduce an undefined semantic dependency.

### G3 — CK-003 closure

Review and integrate only evidence that survives independent verification:
- DQ-002 hash-domain decision and cross-language fixture.
- DQ-003 version semantics and binding fixture.
- DQ-004 event-type semantics.
- Remaining DQ gates required by the current evidence program.

### G4 — Executable conformance

Turn the specification into machine-checkable contracts: fixtures, RI-PY tests, RI-RS tests, shared expected values, and a deterministic conformance runner.

### G5 — CI enforcement

Add repository-native GitHub Actions that run specification validation and conformance checks. CI must fail closed on normative regressions. Payment/plan limitations must be treated as environment evidence, not as a false PASS.

### G6 — Traceability and release readiness

Produce a complete APS → INV → CONF → FIX → Evidence → RI → Release matrix. Close only those rows with objective evidence. Publish a release-readiness report and leave unresolved items explicitly marked OPEN/BLOCKED.

## 4. Non-negotiable completion criteria

The repository is **not complete** merely because documents exist. Completion requires:

1. APS-001 is authored and formally approved by the project owner/Chief Architect.
2. No contradictory normative semantics remain across APS documents.
3. All 15 invariants have explicit verification methods and executable conformance coverage.
4. Reference fixtures have stable, versioned expected values.
5. RI-PY and RI-RS agree on all shared canonical fixtures where interoperability is required.
6. Hash-domain semantics are explicit and bound to canonical bytes.
7. Version semantics are explicit and testable.
8. Traceability is complete from requirement to release evidence.
9. CI executes the conformance gate.
10. Any external/environmental blocker is reported as BLOCKED rather than converted into PASS.

## 5. Execution discipline

No production implementation in Core or Guard is modified as a side effect of completing this specification repository. Specification closure precedes implementation remediation. Once the specification is stable, Core and Guard are brought into conformance against it.

## 6. Immediate execution backlog — NOW

The following backlog defines the work that is actionable **now**, before full schema closure, conformance automation, or release work.

### WP-1 — APS-001 gap list

**Status:** CLOSED
**Goal:** make APS-001 the stable reference point for every downstream correction.

Tasks:
1. Review APS-001 section-by-section against the Constitution and existing APS dependencies.
2. Mark each section as `READY FOR REVIEW`, `OPEN`, or `BLOCKED`.
3. Record where APS-001 depends on unresolved APS-200 / APS-300 contracts, DQ-003 version semantics, or DQ-004 event-type semantics.
4. Produce one consolidated gap list rather than rewriting the full document.

Expected output:
- a concise APS-001 gap register with per-section status
- explicit list of unresolved contract dependencies

#### WP-1 deliverable — APS-001 section gap register

| APS-001 section | Status | Current assessment | Primary dependency / blocker |
|---|---|---|---|
| §1 Protocol Identity and Scope | READY FOR REVIEW | Mission, protocol identity, and scope boundary are consistent with the Constitution. | Architecture Review / approval only |
| §2 Protocol Execution Model | OPEN | Execution flow is coherent, but the binding between execution profile, audit record, and evidence lifecycle still needs tighter downstream reconciliation. | APS-200 / APS-300 cross-references |
| §3 Input Requirements | BLOCKED | Request validity depends on exact `ENT-002` schema, field constraints, numeric contract, and version-compatibility behaviour that are not fully closed. | APS-200 schemas; DQ-003 |
| §4 Output Requirements | BLOCKED | Result requirements are directionally clear, but the exact `ENT-003` contract and canonical decision vocabulary are still unresolved. | APS-200 `ENT-003` closure |
| §5 Policy Model | OPEN | Reproducibility and fail-closed semantics are stable, but canonical policy identity/version semantics need tighter binding. | DQ-003; APS-200 `ENT-004` |
| §6 Evidence Generation Requirements | BLOCKED | Required evidence fields are listed, but exact Evidence Pack structure, attestation contract, and profile boundaries remain incomplete. | APS-300 pack schema; `ENT-006`; Evidence Profiles |
| §7 Cryptographic Requirements | OPEN | Canonical-byte and hash-domain wording is materially stable, but full Merkle-profile closure and conformance evidence promotion remain incomplete. | DQ-002 scope; DQ-006 residuals |
| §8 Error Handling | OPEN | Fail-closed behaviour is defined, but compatibility exceptions and error classification still depend on downstream harmonization. | APS-100 / APS-200 / version rules |
| §9 Conformance Requirements | BLOCKED | The conformance gate is defined, but mandatory PASS evidence does not yet exist for fixtures, runner, and full matrix execution. | APS-400 / APS-500 / runner / CI |
| §10 Normative Authority | READY FOR REVIEW | Hierarchy is explicit and consistent with the Constitution. | Downstream citation cleanup only |
| §11 Traceability | OPEN | The required chain is correct, but APS-001 requirements are not yet exhaustively mapped to invariant-level verification rows. | APS-900 traceability completion |
| §12 Version Binding | BLOCKED | The section requires an explicit compatibility matrix that does not yet exist as a settled normative contract. | DQ-003 |
| §13 Release Gate | BLOCKED | The release gate is directionally correct, but fixtures, runner, CI, release evidence, and approval records are not yet in place. | APS-500 corpus; runner; CI; review evidence |
| Appendix A — Open closure dependencies | OPEN | The blocker list is substantially correct and should remain the single short list for APS-001 approval gating. | Must stay synchronized with DQ-003 / DQ-004 / APS-200 / APS-300 / CI state |

#### WP-1 — stable vs unresolved areas

Stable enough for review:
- §1 Protocol Identity and Scope
- §10 Normative Authority
- the core constitutional posture of APS-001 as a normative draft

Open but not fully blocked:
- §2 Protocol Execution Model
- §5 Policy Model
- §7 Cryptographic Requirements
- §8 Error Handling
- §11 Traceability
- Appendix A maintenance and synchronization

Blocked by unresolved downstream contracts:
- §3 Input Requirements
- §4 Output Requirements
- §6 Evidence Generation Requirements
- §9 Conformance Requirements
- §12 Version Binding
- §13 Release Gate

#### WP-1 — immediate dependency set

The smallest dependency set now controlling APS-001 approval readiness is:

1. machine-readable APS-200 entity schemas
2. exact APS-300 Evidence Pack schema and Evidence Profile boundaries
3. DQ-003 version-compatibility semantics
4. DQ-004 event-type semantics and approved registry entries
5. canonical APS-500 fixture corpus
6. executable cross-language conformance runner
7. repository-native CI gate
8. Architecture Review / Chief Architect approval record

#### WP-1 — next correction queue triggered by this register

1. APS-200 — close `ENT-002`, `ENT-003`, `ENT-004`, `ENT-006`, `ENT-007`, version-binding, and machine-readable schema gaps
2. APS-300 — close Evidence Pack structure, attestation linkage, and Evidence Profile definitions
3. APS-100 / APS-400 / APS-500 — align conformance language with the real fixture and execution state
4. APS-900 — complete APS-001 requirement-to-traceability mapping
5. CK-003 DQ-003 / DQ-004 blocker records — settle version and event-type semantics needed by APS-001 approval

### WP-2 — APS reconciliation pass

**Status:** OPEN
**Goal:** identify the first downstream documents that must change once APS-001 gaps are agreed.

Priority order:
1. APS-100
2. APS-200
3. APS-300
4. APS-400
5. APS-500
6. APS-900
7. APS-950

Tasks:
1. Check each document's authority chain and APS-001 references.
2. Find MUST-level requirements without a single clear path to `INV / CONF / FIX / EVID`.
3. Record semantic conflicts in versioning, canonical bytes, evidence, identity, audit record, and policy semantics.
4. Produce an ordered correction list for the next edit wave.

Expected output:
- ordered reconciliation queue for APS-100/200/300/400/500/900/950
- list of must-fix semantic conflicts

#### WP-2 deliverable — initial reconciliation pass for APS-100 / APS-200 / APS-300

This first WP-2 pass covers the highest-priority normative dependencies reviewed directly against APS-001.

| Document | Authority-chain assessment | Missing or weak traceability path | Must-fix semantic conflicts | Correction priority |
|---|---|---|---|---|
| APS-100 | Authority citation to APS-001 is correct, but the document body no longer matches the current APS-400 / registry state. | `§3` still shows no CONF assignment for `INV-007`, `INV-012`, `INV-013`, `INV-014`, `INV-015`; `§5` traceability order differs from APS-001 / APS-900; the catalogue entries do not carry the verification/evidence detail that `§2` says every invariant MUST define. | stale invariant-to-CONF catalogue; APS-100's own structure requirements are satisfied only in the registry, not in the APS-100 body; compliance wording assumes invariant PASS status without defining a canonical invariant-status model. | HIGH |
| APS-200 | Authority chain is directionally correct and now carries the DQ-006 serialization closure, but several required contracts are still only partial. | No exact machine-readable schema set for `ENT-001…ENT-008`; `ENT-004` has no CONF mapping in `§10`; `execution_id`, `request_fields`, decision vocabulary, and attestation lifecycle remain TODO-level contracts. | `object_id` allows `UUID v4 or canonical format`, which is too loose for INV-015 / APS-001 identity semantics; `ENT-007.event_type` depends on a registry with no approved tokens yet (DQ-004 blocker); evidence / attestation / audit relationships remain under-specified for APS-001 approval. | CRITICAL |
| APS-300 | Authority chain is correct and cryptographic byte-domain binding is materially aligned with APS-200 §8. | No exact Evidence Pack container contract; no defined Evidence Profiles; no explicit required field linking evidence to the APS requirement(s) it documents even though INV-005 / APS-001 §6 require that traceability. | `evidence_id` is fixed to UUID v4, which may conflict with the unresolved canonical-identity contract; `attestation_reference` is mandatory while `ENT-006` lifecycle/authority is unresolved in APS-200; verification claims conformance/invariant verification without a fully specified pack/linkage model. | CRITICAL |

#### WP-2 — reconciliation conclusions from this first pass

1. **APS-200 is the first correction target.**
   APS-001 blockers for input, output, policy-reference, audit-record, identity, and version-binding semantics all terminate in APS-200 gaps.

2. **APS-300 is the second correction target.**
   APS-001 evidence-generation and release-gate blockers cannot close until the Evidence Pack, attestation linkage, and Evidence Profile boundaries are explicit.

3. **APS-100 needs alignment after APS-200 / APS-300 stabilization.**
   Its largest issues are catalogue staleness and mismatch with the current registry / APS-400 state, not the absence of an authority chain.

#### WP-2 — ordered correction queue triggered by these findings

1. APS-200
   - tighten canonical identity semantics for `object_id` / `object_type`
   - close `execution_id`, `request_fields`, decision vocabulary, and attestation lifecycle contracts
   - complete entity-to-CONF traceability, especially `ENT-004` and `ENT-007`
   - convert entity contracts into machine-readable schemas
2. APS-300
   - define the Evidence Pack container and linkage model
   - add the missing requirement-to-evidence traceability field/contract needed by INV-005
   - define Evidence Profiles and attestation expectations
3. APS-100
   - reconcile the invariant catalogue with CONF-011…CONF-015
   - align APS-100 traceability wording with APS-001 / APS-900
   - decide whether APS-100 itself or the registry is the authoritative home for invariant verification/evidence detail

### WP-3 — CK-003 blocker register

**Status:** OPEN
**Goal:** separate normative decisions from working evidence and unresolved closure gates.

Tasks:
1. List all DQ items still blocking release-readiness.
2. Separate already-bound normative decisions from working evidence and unresolved closure requirements.
3. Treat DQ-003, DQ-004, and DQ-006 residuals as the immediate blocker set.
4. Keep DQ-002 in scope only where it changes the normative contract.

Expected output:
- one CK-003 blocker register using only `OPEN / BLOCKED / READY / CLOSED`
- explicit minimum DQ set required before schema + conformance promotion

### WP-4 — Traceability gap pass

**Status:** OPEN
**Goal:** make every invariant traceability state explicit before claiming closure progress.

Tasks:
1. Walk `INV-001` through `INV-015`.
2. Confirm for each invariant: APS source, CONF assignment, fixture status, expected evidence type, and RI relevance.
3. Mark the weakest missing link as exactly one of: `OPEN`, `BLOCKED`, `READY`, `NOT VERIFIED`.

Expected output:
- a working traceability gap register with one row per invariant
- no unstated assumptions about fixture or evidence readiness

### WP-5 — Fixture promotion plan

**Status:** OPEN
**Goal:** distinguish placeholders and working corpus artifacts from candidate normative fixtures.

Tasks:
1. Classify each current fixture as `PLACEHOLDER`, `WORKING`, or `CANDIDATE NORMATIVE`.
2. Identify the minimum fixture set needed for a first meaningful conformance run.
3. Record fixture dependencies on APS-200 schemas, APS-300 pack structure, and specific CONF procedures.

Expected output:
- fixture promotion table covering `FIX-001`, `/fixtures/corpus/`, and `/fixtures/ck003/`
- explicit minimum fixture set for early conformance execution

### WP-6 — Minimum automation plan

**Status:** OPEN
**Goal:** sequence safe automation work without freezing unstable contracts too early.

Implement now:
1. `check-doc-headers.sh`
2. `check-ids.sh`
3. `check-traceability.sh`

Defer until schemas and canonical formats stabilize:
- `validate-fixtures.sh`
- `generate-traceability-matrix.py`

Expected output:
- phased automation order with prerequisites
- explicit defer list for schema-dependent tooling

## 7. Immediate execution order

1. WP-1 — APS-001 gap list
2. WP-2 — APS-100/200/300 reconciliation
3. WP-3 — CK-003 blocker register
4. WP-4 — INV → CONF → FIX traceability pass
5. WP-5 — fixture promotion plan
6. WP-6 — minimum automation plan

## 8. Exit criteria for the NOW stage

The NOW stage is complete only when:

1. APS-001 has a concrete per-section gap list.
2. The next APS correction queue is ordered and justified.
3. CK-003 has an explicit blocker register.
4. Every invariant has an explicit traceability state.
5. Fixtures are separated into placeholder / working / candidate normative sets.
6. Automation order is defined without prematurely locking unstable schemas or formats.
