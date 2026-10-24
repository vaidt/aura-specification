# AURA Stabilization — Execution Ledger (2026-10-24)

**Classification:** Operational, non-constitutive.  
**Baseline:** Supplied AURA Watch reports dated 2026-10-24; live GitHub reads are recorded below where available.  
**Invariant:** No direct main changes, merges, bypass modifications, bootstrap dispatch, or governance promotion were performed in this work session.

## 1. Delivered artifacts

| Artifact | Location | State |
|---|---|---|
| Stabilization plan and priority queue | [PR #43](https://github.com/vaidt/aura-specification/pull/43) | Draft/open |
| Gate/evidence matrix | Included in [PR #43](https://github.com/vaidt/aura-specification/pull/43) | Draft/open |
| Guard PR #13 review checklist | [PR #19](https://github.com/vaidt/aura-guard-v1.3/pull/19) | Draft/open |
| Core PR #6 review checklist | [PR #9](https://github.com/vaidt/aura-poc-a-core-v3.3/pull/9) | Draft/open |
| RI-RS evidence serialization analysis | [PR #20](https://github.com/vaidt/aura-guard-v1.3/pull/20) | Draft/open |
| C6 JCS workflow/test-boundary repair candidate | [PR #44](https://github.com/vaidt/aura-specification/pull/44) | Draft/open |

These are not releases, ratifications, or approvals to merge.

## 2. Operational plan PR #43

Contains:
- P0 repository and branch-control inventory;
- ASIG bypass review with separate interpretation of AURA-ADM rules;
- exact-head review requirements for Guard #13 and Core #6;
- isolated repairs for C6 reference paths, environment setup and evidence serialization;
- exact source/corpus pins and independently validated C6 evidence contract;
- source-of-truth repository map;
- upstream CodeQL diagnostic;
- Bootstrap pause criteria;
- governance evidence requirements for M1/G0/G1/P-008 and DQ-006/CONF-003;
- evidence ledger fields, definitions and exit criteria.

## 3. Live technical actions on the C6 experimental path

On the existing experimental head branch used by PR #41, commits were made to correct three malformed relative paths and make the JCS test step's test ownership explicit. The relative paths were then found to be interpreted differently by the repository reference checker; the follow-up candidate PR #44 uses explicit GitHub links and has a passing Draft Conformance/reference-hygiene run.

On PR #44's candidate head, the workflow was narrowed to:
- `test_python_jcs_probe.py`;
- `test_jcs_multivector_corpus.py`;
- an explicit six-vector adapter comparison command;
- an allowed pull-request base branch so the workflow can trigger on the C6 integration branch.

Draft Conformance run [40105955951](https://github.com/vaidt/aura-specification/actions/runs/40105955951) and run [40105952634](https://github.com/vaidt/aura-specification/actions/runs/40105952634) passed on head `9dcabf3b324c17e4eabbc2013784b7a235214a79`; these are **Draft Conformance**, not JCS adapter results. At time of ledger authoring, a JCS multi-vector run on the final PR #44 head had not been confirmed. Therefore the workflow/test repair remains unvalidated by its intended workflow.

## 4. RI-RS artifact discrepancy analysis

For Guard run [40048516275](https://github.com/vaidt/aura-guard-v1.3/actions/runs/40048516275), the preservation log reports `Extra data: line 18 column 2 (char 809)`. The downloaded uploaded artifact contains a strictly parseable `ri-rs-results.json` with 27 unique cases, all `matched=true`, no mismatches, and a report hash equal to `d89dc3c80727460d763cbda7686fd5ec3c6b91cb24110f3c6e3bee718a4c25ec`. Its `index_sha256` equals the SHA-256 of the exact included index artifact, `445d5808cb76a24b916a91e91636d4ce10ac3b0239f9eb2f474264783bc41181`.

This is a real inconsistency between logged preservation and uploaded report contents. Root cause is **not proven**. PR #20 records an exact diagnostic sequence; no workflow/code change was made to guess around it.

## 5. Branch-control read

For `vaidt/Projekt-Aura-BETA-`, the full ruleset reads confirm:
- ASIG ruleset #25504515 is active for all branches and has a DeployKey bypass actor with mode `always`;
- AURA-ADM ruleset #25505024 is active on `refs/heads/main`, requires three named checks and has no bypass actors.

The two rulesets are distinct; ASIG bypass must not be inferred to bypass AURA-ADM. Ruleset listing in spec/Guard/Core returned no repository rulesets, but classic branch-protection endpoints were forbidden to the connected integration. Therefore classic protection state is **not independently proven by these reads** and must be verified by an actor with the necessary permissions. Private Bootstrap ruleset endpoint also returned an access/plan limitation. No ruleset was changed.

## 6. Current gate disposition

The latest conformance report retained:
- CONF-003: OPEN;
- CONF-007: BLOCKED;
- CONF-009: OPEN.

The independent source reports remain:
- DQ-006: OPEN;
- CONF-003: PARTIAL;
- C6: BLOCKED_NOT_EXECUTED / BLOCKED_PENDING_EVIDENCE_REVIEW;
- M1: BLOCKED / NOT PROVEN;
- G0: NOT PROVEN;
- G1: BLOCKED;
- P-008: CONFLICTED / NOT ESTABLISHED;
- Bootstrap Control PR #1: paused, no dispatch.

Nothing in these engineering/documentation changes changes those states.

## 7. Next executable steps

1. Confirm the JCS multi-vector workflow runs on the latest PR #44 head; inspect all steps and artifact before interpreting its result.
2. If the workflow does not run or fails, repair only the demonstrated trigger/job/test defect and retain Draft status.
3. Continue the controlled review of Guard #13 and Core #6; obtain independent review and prove effective branch controls before any authorized merge.
4. Update dependent experimental PR bases only after the corresponding maintenance change is accepted; rerun each affected workflow on its exact head.
5. Implement the RI-RS evidence-path fix only after instrumenting the actual path, byte count and hash parsed within the same job.
6. Obtain a permission-capable branch protection read for the remaining repositories, and independently verify trusted required-check provenance in Issue #8.
7. Keep Bootstrap paused and governance gates unchanged until primary constitutive evidence supports a state transition.

**Exit rule:** No state is moved by inference. A scoped workflow pass is recorded as scoped technical evidence; only complete, repeatable, independently reviewed evidence can support a technical gate decision, and only the proper governance process can establish normative effect.
