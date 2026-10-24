# AURA Stabilization Control Plan — 2026-10-24

**Status:** Draft operational plan  
**Authority:** Non-constitutive. This document does not ratify protocol semantics, establish authority continuity, authorize release, or change governance state.  
**Baseline source:** AURA Repo & CI Watch reports supplied for 2026-10-24. Repository state must be re-read before acting on any gate.  
**Operating mode:** Preserve fail-closed behavior. No direct edits to `main`, no bypass of branch protections, no auto-merge, no bootstrap dispatch, and no governance status transition based solely on CI.

## 1. Executive disposition

AURA enters **controlled stabilization**. Work should reduce verified risk and close evidence-generation defects before expanding experimental Stage C scope.

Three independent decision tracks must remain separate:

1. **Repository integrity and release hygiene** — effective protection of default branches, trusted required-check provenance, reviewed maintenance fixes.
2. **Technical conformance** — reproducible JCS/Merkle/wire-consumer tests, exact source and corpus pins, complete machine-readable evidence.
3. **Governance and authority** — evidence of role, authority, continuity, and effective ratification. CI results are technical evidence only and are not constitutive acts.

## 2. Work queue and exit criteria

| ID | Priority | Work item | Required evidence / exit criterion | Prohibited inference |
|---|---|---|---|---|
| STAB-001 | P0 | Capture repository baseline and effective branch controls | Record repository, default-branch SHA, active rulesets/protection, included refs, required checks, bypass actors/modes, and a read-back proving the effective configuration | A visible active ruleset alone does not prove all merge paths are protected |
| STAB-002 | P0 | Resolve ASIG bypass scope in `vaidt/Projekt-Aura-BETA-` | Establish whether DeployKey bypass is required; narrow or remove only after impact assessment; verify effective policy after any authorized change | Do not infer that ASIG bypass necessarily bypasses the separate AURA-ADM ruleset |
| STAB-003 | P1 | Review Aura-Guard PR #13 security dependency patch | Re-read exact head, inspect lockfile-only diff and checks; verify `cargo-audit`, `cargo-deny`, build/test and integration controls on the exact head; independent review; after authorized merge, re-read `main` and rerun required checks | PR-head success does not mean `main` is remediated; leave Draft until its stated validation criteria are met |
| STAB-004 | P1 | Review Core PR #6 test dependency installation fix | Re-read exact head and workflow diff; ensure full pytest actually executes to completion with no skipped tests; independent review; after authorized merge, re-run the checks on updated `main` | A green dependent PR based on old `main` does not inherit PR #6's result |
| STAB-005 | P1 | Repair Stage C local documentation references | Reference checker passes on the exact candidate commit and no required conformance runner is skipped due to broken links | A skipped runner is not a PASS |
| STAB-006 | P1 | Fix RI-PY environment preflight | Explicitly define and validate `AURA_RI_PY_ROOT`; fail with a clear configuration error before test collection when absent | A test setup KeyError is not a byte-comparison mismatch |
| STAB-007 | P1 | Fix RI-RS results serialization | Emit exactly one schema-valid JSON document to the result path; parse the complete file strictly; verify required keys, case counts, source pins, and corpus identity | Do not parse only the first JSON value or suppress trailing-data errors |
| STAB-008 | P1 | Execute one pinned C6 end-to-end run | Pin source commits/blob hashes and shared-corpus digest; RI-PY and RI-RS results both complete; all required cases match; evidence artifact validates independently; preserve logs and artifact digests | Unit tests or partial job success cannot close C6 |
| STAB-009 | P2 | Rebase/revalidate experimental consumers after maintenance fixes | Each PR's base/head SHA is explicit; rerun its own required suite after any base change; review diff before declaring readiness | Never transfer CI evidence across different SHAs without proof that the tested inputs are identical |
| STAB-010 | P2 | Establish source-of-truth repository map | Document canonical repository and synchronization/backport rules for specification, Core, Guard, historical/upstream mirrors | Ahead/behind counts do not establish normative authority |
| STAB-011 | P1 | Diagnose upstream CodeQL failure | Capture exact workflow run, job, step logs, event, SHA, permissions and failure class; propose a narrowly scoped correction | Do not guess root cause from an unavailable log |
| STAB-012 | P0 | Keep Bootstrap Control PR #1 paused | Require effective branch protection, independent review, workflow results on exact head, digest-pinned images, controlled package versions, and explicit authorization before any dispatch | No dispatch or merge while required gates are unproven |
| GOV-001 | P0 | Keep M1/G0/G1 and P-008 fail-closed | Collect primary constitutive evidence for identity-to-role binding, competence grant, continuity, scope, and ratification; independently verify the exact artifact/version and signature | CI, commit history, a custodian note, or key possession alone does not prove authority or ratification |
| GOV-002 | P1 | Reassess DQ-006 and CONF-003 only against documented acceptance criteria | Trace each residual to required evidence and independent review; update statuses only when the authoritative register and proof package support it | Do not infer closure from bounded fixtures or workflow status |

## 3. C6 failure taxonomy

The reported failures are independent and must be tracked separately:

- **Broken local references:** repair the paths or missing targets; rerun the complete reference check.
- **Missing `AURA_RI_PY_ROOT`:** define the variable explicitly in workflow setup and add a preflight assertion.
- **Malformed `ri-rs-results.json`:** make one owner responsible for producing a single JSON document. Logs must go to a separate stream/file. Strictly parse the complete artifact, reject trailing content, validate schema and compare expected case count to actual case count.
- **Dependency/format failures in Guard experimental branches:** re-run on the exact candidate after the security maintenance fix is available; do not weaken audit/deny/format gates.
- **Partial conformance success:** preserve as limited evidence only. Record exactly which vectors, implementations and paths were exercised.

## 4. C6 evidence contract

A candidate C6 evidence package should contain:

1. immutable identifiers for repository and commit SHA for each consumer;
2. content/blob digests for relevant source and configuration;
3. shared corpus identifier, manifest and SHA-256;
4. per-case expected and actual result, stable rejection code where applicable, input digest and byte length;
5. schema-valid RI-PY and RI-RS machine-readable reports;
6. runner/workflow identity, run URL/ID, job result and relevant logs;
7. digest of the complete evidence artifact;
8. independent validation outcome and reviewer identity;
9. an explicit statement that the package's authority, governance, authorization, and release effects are NONE unless separately established by the governing process.

The validator must fail closed on missing fields, source-pin drift, corpus mismatch, duplicate cases, missing cases, malformed JSON, trailing content, inconsistent case counts, digest mismatch, or any unexpected test skip.

## 5. Merge discipline

For PR #13 and PR #6, use this sequence:

1. Re-read PR, exact head SHA, base SHA, changed files, reviews, and required checks.
2. Inspect the diff and check that the actual change remains within the stated scope.
3. Verify every required job completed on the exact head. No inferred success from a different run or SHA.
4. Obtain independent review and ensure effective main protection is established.
5. Merge one PR at a time only if the authorized human decision and repository controls permit it.
6. Read back the resulting `main` SHA, verify the merged diff, and run the required suite against that new SHA.
7. Revalidate dependent PRs whose base/inputs changed.

This plan does not authorize a merge by itself. Keep both changes open until their gates and authorized decision are satisfied.

## 6. Repository protection review checklist

For every in-scope default branch, record and verify:

- effective rulesets and classic protection, including ref scope;
- required status checks and the identity/provenance of the check publisher;
- review count, approval of the latest push where required, and resolved review threads;
- signed commit requirements and linear history if applicable;
- force-push and branch-deletion restrictions;
- every bypass actor, mode and reason;
- a read-back of effective configuration after any authorized adjustment;
- an adversarial negative test showing PR-controlled duplicate check names cannot satisfy a trusted gate.

The presence of status-check names alone is insufficient if a contributor can produce synthetic jobs with those names. Issue #8 remains unresolved until source-bound provenance is demonstrated by a controlled test.

## 7. Governance invariants

- `M1 = BLOCKED / NOT PROVEN` remains until primary constitutive evidence demonstrates authority continuity.
- `G0/G1 = NOT PROVEN / BLOCKED` remain until their applicable proof requirements are satisfied.
- `P-008` remains `CONFLICTED / NOT ESTABLISHED` unless a valid and properly authorized ratification is proven.
- `DQ-006 = OPEN` and `CONF-003 = PARTIAL` remain unchanged until each defined residual has required evidence and review.
- A technical PASS never automatically updates a governance state.
- No Bootstrap dispatch, production promotion, or release authorization follows from this operational plan.

## 8. Daily evidence ledger

For each action record:

| Field | Requirement |
|---|---|
| Work item | Stable identifier from this plan |
| Observed at | UTC timestamp |
| Repository / ref | Fully qualified repository and branch/tag |
| Commit | Full SHA, not abbreviated |
| Workflow | Run ID/URL, job IDs and conclusion |
| Evidence | Artifact path/URL and SHA-256, if applicable |
| Result | PASS / FAIL / BLOCKED / NOT RUN, with exact scope |
| Reviewer | Identity and nature of review |
| Decision | Technical-only or governance decision, explicitly distinguished |
| Residuals | Open questions and next acceptance criterion |

## 9. Immediate execution order

1. Read-only baseline snapshot and PR revalidation.
2. Independent scope and CI review for PR #13 and PR #6; no merge until required gates and authorization are confirmed.
3. Repair the three C6 workflow defects (references, environment preflight, JSON report) in isolated changes.
4. Run the complete pinned C6 workflow and independently validate the evidence artifact.
5. Complete source-bound required-check provenance investigation (Issue #8) and branch-control inventory.
6. Pursue primary constitutive governance evidence in parallel without changing the blocked statuses.

**Exit condition for stabilization:** known technical blockers are either resolved with exact, reproducible evidence or explicitly tracked with an owner and acceptance criterion; repository protection is verified; C6 has a complete independently validated evidence package; governance statuses reflect only qualifying evidence. This is not equivalent to production readiness or release approval.
