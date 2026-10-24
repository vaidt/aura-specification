# AURA Evidence and Gate Matrix — 2026-10-24

**Status:** Draft operational register. Non-normative and non-constitutive.
**Rule:** Every state below is a snapshot from the supplied 2026-10-24 AURA Watch reports, not a new finding. Re-read live repository state before acting.

| Gate / workstream | Reported state | Evidence currently available | Missing / next action | Permitted transition |
|---|---|---|---|---|
| Default-branch protection inventory | PARTIAL / NOT PROVEN across reported repos | AURA-ADM and ASIG ruleset details for `vaidt/Projekt-Aura-BETA-`; four other `main` branches reported without visible protection | Inventory active rulesets, ref scope, bypass actors, required checks, reviews and negative-test evidence for each repo | Mark verified only after effective configuration read-back and controlled validation |
| ASIG bypass scope | OPEN / REVIEW REQUIRED | Ruleset #25504515 contains DeployKey bypass `always`; AURA-ADM ruleset #25505024 is separate and has no bypass actors in report | Establish necessity and scope; assess effects; authorized adjustment only; read back effective rulesets | Close only when bypass is removed or narrowly justified and the full effective path is validated |
| Issue #8 trusted-check provenance | OPEN / UNRESOLVED | Controlled test reportedly allowed PR-controlled duplicate status names; synthetic M1 check failure still blocked | Bind check to approved workflow/source; perform controlled adversarial test; preserve M1 failure gate | Close only when duplicate PR-controlled contexts cannot satisfy trusted check and real verifier remains effective |
| Aura-Guard PR #13 | OPEN / DRAFT | Reported green security/build/integration checks on head `dd08cf46677153295511b2691e3da0aea5d13c25` | Re-read exact CI and diff; independent review; confirm branch protections; authorized merge decision; post-merge checks | Technical maintenance closure only after the merged main SHA is checked; governance unaffected |
| Core PR #6 | OPEN | Reported full pytest/Docker/ARM64/x86_64/WASM/determinism success on `0e10964703c1e0273094b274d0969d422deab9f2` | Review workflow diff, prove full suite execution/no skips; independent review; authorized merge; post-merge tests | Technical maintenance closure only; downstream PRs need their own reruns |
| Spec Stage C PR #37 (C1) | OPEN / DRAFT | Adapter invocation contract; one baseline JCS vector documented in PR description | Review schema, source/engine provenance and bounded scope; ensure failures fail closed | No normative effect; do not equate adapter test with full conformance |
| Spec Stage C PR #38 (C4) | OPEN / DRAFT | Bounded six-vector isolated adapter comparison described as successful | Confirm exact latest run/head; review vector coverage and evidence artifact | Bounded adapter result only; cannot close RFC 8785 or C6 |
| Spec Stage C PR #39 (C5) | OPEN / DRAFT | Merkle corpus/oracle work described in PR | Review domain separation, tree sizes, proof vectors, negative controls and production-path limits | Do not claim RI-PY production tree/proof parity unless implementation surface supports it |
| Spec Stage C PR #40 (C6 preflight) | OPEN / DRAFT | Negative-test preflight experiment | Inspect exact run and contract; validate all required inputs/outputs | Preflight alone does not close C6 |
| Spec Stage C PR #41 (strict wire) | OPEN / DRAFT / CI FAILURE | Python tests and two comparisons passed; broken local references and missing `AURA_RI_PY_ROOT` blocked other jobs per report | Repair refs and environment preflight; rerun complete workflow on exact head | No C6 closure from partial runs |
| Guard PR #16 | OPEN / DRAFT / CI FAILURE | Build/test, Clippy, Gate 3/4 and stress/replay reportedly pass; audit/deny/rustfmt fail; RI-RS evidence parse failure | Keep all policy gates; revalidate dependency graph after #13 is accepted; fix JSON generation and strictly parse whole report | No C6 closure until full required workflow + evidence validation pass |
| Guard PR #18 | OPEN / DRAFT / CI FAILURE | Alternative consumer experiment; build/test/integration reported pass, audit/deny/rustfmt failures reported | Avoid duplicate divergent implementations without reason; compare diffs; rerun policy gates after dependency baseline is corrected | No runtime wiring or release effect without separate review |
| Core PR #7/#8 | OPEN / EXPERIMENTAL | Dedicated checks reportedly pass; full pytest fails due to missing `rfc8785` on base | Rebase/recreate from updated main after PR #6 outcome; run entire test suite on own head | No inherited PASS from PR #6 |
| C6 end-to-end | BLOCKED / BLOCKED_PENDING_EVIDENCE_REVIEW | Some JCS and mutation tests pass; full workflow/report path does not | Pin consumer commits, corpus digest, configuration; execute all cases in RI-PY and RI-RS; validate reports and artifact digest independently | C6 may change only after complete, reproducible and independently reviewed package |
| DQ-006 | OPEN | Register retains authority-boundary, upstream reachability and ratification residuals | Map each residual to a required primary evidence and reviewer | Remains OPEN until all defined residuals close with acceptable evidence |
| CONF-003 | PARTIAL | Bounded CANONICAL-003 results and limited RI-RS testing | Complete prohibited-input scope, source boundary and required evidence path | Partial results do not imply full gate PASS |
| M1 authority continuity | BLOCKED / NOT PROVEN | Historical custodian docs are noted but not constitutive proof per report | Primary evidence of identity-role binding, competence grant, continuity and scope | No status change based on CI or self-referential records |
| G0 / G1 | NOT PROVEN / BLOCKED | No new constitutive evidence in the report | Gather and independently assess evidence required by the applicable governance contract | Remain blocked until proven |
| P-008 | CONFLICTED / NOT ESTABLISHED | No new effective ratification reported | Resolve semantic conflict and produce valid authorized ratification evidence | No implementation authorization or normative effect inferred |
| Bootstrap Control PR #1 | OPEN / DRAFT / PAUSED | Head `77ef72aed164f308dafed1d0b78a12d792340c5c`; zero independent reviews and no workflow run on exact head per report | Effective protection, independent review, exact-head CI, image digest pins, controlled OS package versions, explicit authorization | Do not dispatch, merge, or treat as approved |
| Upstream CodeQL | FAILURE / ROOT CAUSE UNKNOWN | Scheduled failure reported for 2026-10-19; logs unavailable in report | Obtain exact job/step logs, workflow SHA, event and permissions | Do not infer cause without logs |
| Upstream PR #62 / #67 | ACTION_REQUIRED | No new CI run in report | Determine required actor/action; trigger only through proper authorized path | Not a failure unless an actual run fails |

## Evidence quality labels

- **PASS — scoped:** a named test passed on a specific commit and inputs.
- **PASS — gate:** the complete defined gate passed on exact inputs, with every mandatory job executed and validated.
- **FAIL:** a mandatory check executed and failed.
- **BLOCKED:** the gate could not complete because a required precondition or evidence step failed.
- **NOT RUN:** no execution evidence exists.
- **NOT PROVEN:** proof required by the governing criteria has not been supplied or validated.

These labels are not interchangeable. Never promote a scoped PASS to a gate PASS or a governance status.
