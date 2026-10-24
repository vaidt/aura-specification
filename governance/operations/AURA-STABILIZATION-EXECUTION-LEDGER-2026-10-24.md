# AURA Stabilization — Execution Ledger (2026-10-24)

**Classification:** Operational, non-constitutive.  
**Baseline:** Supplied AURA Watch reports dated 2026-10-24 plus live GitHub reads on 2026-10-24.  
**Invariant:** No direct main changes, merges, bypass modifications, bootstrap dispatch, or governance promotion were performed in this work session.

## 1. Delivered artifacts and PRs

| Artifact | Location | State |
|---|---|---|
| Stabilization plan, gate matrix, execution ledger | [PR #43](https://github.com/vaidt/aura-specification/pull/43) | Draft/open |
| Guard PR #13 review checklist | [PR #19](https://github.com/vaidt/aura-guard-v1.3/pull/19) | Draft/open |
| Core PR #6 review checklist | [PR #9](https://github.com/vaidt/aura-poc-a-core-v3.3/pull/9) | Draft/open |
| RI-RS serialization diagnosis | [PR #20](https://github.com/vaidt/aura-guard-v1.3/pull/20) | Draft/open |
| JCS test trigger/ownership candidate | [PR #44](https://github.com/vaidt/aura-specification/pull/44) | Draft/open; bounded JCS result independently verified |
| RI-RS exact-byte preservation candidate | [PR #21](https://github.com/vaidt/aura-guard-v1.3/pull/21) | Draft/open; CI incomplete/blocked |

These are not releases, ratifications, or approvals to merge.

## 2. JCS — exact-head run and artifact independently verified

Manual workflow run: [#40106692164](https://github.com/vaidt/aura-specification/actions/runs/40106692164)  
Workflow: `Stage C JCS multi-vector adapter comparison`  
Event: `workflow_dispatch`  
Specification source SHA: `a0804a1968315aae2e8d2d73c4b34f8fcc0fcf78`  
Pinned Rust adapter SHA: `31a7eeab861094fbecc82e8a61351fac49dffe43`  
Job: `120909746178` — all nine workflow steps PASS.  
Artifact: `stage-c-jcs-multivector`, ID `12564597727`, size 37,230 bytes, SHA-256 `d46589e9f617799861642eb47e73a729fb126ea90b987f175c5fb431ba003742`.

The artifact was downloaded and verified independently:
- `comparison.json` reports schema `AURA-STAGE-C-JCS-MULTIVECTOR-EXECUTION-REPORT/0.1`, run ID `40106692164-1`, 6 vectors, `all_engineering_assertions_passed=true`, zero failing vectors;
- on every vector, Python and Rust `canonical.bin` files are byte-identical;
- all six SHA-256 values and output lengths match the committed expected bytes;
- each response carries the same run ID, correct fixture ID/input hash, and expected source commit for its implementation;
- Python engine is `rfc8785 0.1.4`; Rust engine is `serde_json_canonicalizer 0.3.2`.

**Disposition:** PASS for this bounded six-vector isolated JCS adapter comparison. The report explicitly says it is not full RFC 8785 or production RI-PY coverage; normative, governance and release effects are NONE. C6 is still blocked pending production receiver paths, Merkle domain/proof tests, protocol-specific negative cases and governance prerequisites.

## 3. Guard #13 — exact-head dependency security review

PR [#13](https://github.com/vaidt/aura-guard-v1.3/pull/13) remains Draft/open on head `dd08cf46677153295511b2691e3da0aea5d13c25`, with zero independent reviews. It is a one-file `Cargo.lock` patch (no `Cargo.toml` or Rust source changes):
- `rustls-webpki 0.103.15 -> 0.103.16`;
- `webpki-roots 1.0.7 -> 1.0.10`;
- `tokio 1.52.3 -> 1.54.1`.

These updates address the known current log findings for RUSTSEC-2026-0382, RUSTSEC-2026-0381 and the Tokio unsound warning RUSTSEC-2026-0386. Historical PR #13 checks on its own head were green, including `cargo-audit` and `cargo-deny`; those results do not transfer to the different RI-RS experiment branch.

I compared `Cargo.lock` at PR #21's base `ad86f02eb4bb2f3479b3b2e3f6b78f26257c44ff` and PR #13 head. `crypto-bigint 0.5.5` and its checksum are identical in both. The current exact-head audit on PR #21 reports RUSTSEC-2026-0387 for that crate in addition to the Web PKI/Tokio findings. **PR #13 alone does not clear the crypto-bigint blocker.** A separate compatible remediation and audit/deny reruns are required; do not suppress the advisory.

## 4. Core #6 — exact-head CI and review

PR [#6](https://github.com/vaidt/aura-poc-a-core-v3.3/pull/6) is open, not Draft, not merged, head `0e10964703c1e0273094b274d0969d422deab9f2`, with zero reviews.

All seven registered checks on that exact head are PASS:
- Cross-platform deterministic comparison;
- CodeFactor;
- mandatory execution checks x86_64;
- mandatory execution checks ARM64;
- production Core serializer CANONICAL-003;
- full pytest with Docker;
- WASM compatibility.

The diff changes only the workflow's dependency installation step to install the project in editable mode plus pytest. **Technical PASS does not equal independent review.** Obtain an independent review before any merge, then verify the resulting `main` SHA and rerun the required suite against that new SHA.

## 5. RI-RS evidence-preservation candidate #21 — root-cause status and current blockers

Prior run [#40048516275](https://github.com/vaidt/aura-guard-v1.3/actions/runs/40048516275) logged `Extra data: line 18 column 2 (char 809)` during evidence preservation. The uploaded report later downloaded from that run is a valid single JSON document with 27 unique cases, each `matched=true`; report SHA-256 `d89dc3c80727460d763cbda7686fd5ec3c6b91cb24110f3c6e3bee718a4c25ec`. Its `index_sha256` matches the included index bytes SHA-256 `445d5808cb76a24b916a91e91636d4ce10ac3b0239f9eb2f474264783bc41181`.

This proves a discrepancy between the old run's preservation error and the subsequently uploaded report contents, **but it does not prove the exact root cause** (the runtime file may have differed from the later uploaded artifact). Candidate PR [#21](https://github.com/vaidt/aura-guard-v1.3/pull/21) logs path, byte count, SHA-256 and parses the same raw byte buffers, then checks schema, index digest, cases and report status without rewriting the report.

Exact head `d34f561261aa987144ea6d285355180fdfd1b9c7`; CI run [#40106587300](https://github.com/vaidt/aura-guard-v1.3/actions/runs/40106587300) completed its `build + test` job successfully:
- PASS: `cargo build --locked --release --all-targets`;
- PASS: `CANONICAL-003` byte/hash evidence step;
- PASS: `cargo test --locked --all-targets`;
- PASS: `clippy`, Gate 3 Core integration, Gate 4 external E2E and D-3 chain evidence export;
- FAIL: `cargo-audit` due to `crypto-bigint 0.5.5` (RUSTSEC-2026-0387), `rustls-webpki 0.103.15` (RUSTSEC-2026-0382), `webpki-roots 1.0.7` (RUSTSEC-2026-0381), and Tokio 1.52.3 warning RUSTSEC-2026-0386;
- FAIL: `cargo-deny` advisory policy; bans, licenses and sources pass;
- FAIL: `rustfmt` due to existing formatting differences in `conformance/strict_wire_c6.rs`, not the new YAML-only preservation step.

### Corrected finding: why the preservation diagnostics artifact is absent

The absent `preservation-diagnostics.json` from run #40106587300 is explained by a workflow-trigger defect, not by a parser rejection in that run. The run was the general `.github/workflows/ci.yml` workflow. The intended `.github/workflows/stage-c-c6-wire-consumer.yml` workflow has `pull_request.branches: [experiment/stage-c-merkle-c5-20261023]`, while PR #21 targets `experiment/stage-c-c6-wire-consumer-20261024`. Therefore its `strict-wire` preservation step did not run for PR #21.

A separate candidate branch `ops/c6-ri-rs-workflow-trigger-20261024` was created with the additional target branch in the filter. GitHub rejected creating a separate Draft PR against the experimental base, so the trigger fix remains an unreviewed branch change; the existing PR #21 was not modified by that trigger attempt. A dedicated `strict-wire` run on the exact head is still required after applying the trigger through an accepted review path.

**Disposition:** PR #21 has passing build, CANONICAL-003 and test jobs but is not fully green. The old `Extra data` root cause is still not proven; a missing prerequisite (workflow never ran) is now confirmed. Keep PR #21 Draft and C6 blocked. No audit/deny policy was relaxed.

## 6. Effective branch protection and Issue #8 provenance

Classic `required_status_checks` endpoints returned `Branch not protected` for `main` in:
- `vaidt/aura-specification`;
- `vaidt/aura-guard-v1.3`;
- `vaidt/aura-poc-a-core-v3.3`.

The queried branch-target ruleset endpoints returned empty rules arrays for those repos. Therefore effective source-bound merge protection is not established for those `main` branches. Do not merge the maintenance PRs until an authorized protection configuration is installed and read back.

In [BETA ruleset AURA-ADM-MAIN-001](https://github.com/vaidt/Projekt-Aura-BETA-/rules/25505024), the ruleset is active on `refs/heads/main`, requires one approval, latest-push approval and resolved review threads, plus three checks:
- `Validate evidence schemas and records`;
- `Observe pinned authority-source signatures (non-constitutive)`;
- `M1 exact-byte signature gate (strict)`.

All three are bound only to integration/App ID `15368` (GitHub Actions); the ruleset has no bypass actors. A separate active ASIG ruleset [#25504515](https://github.com/vaidt/Projekt-Aura-BETA-/rules/25504515) has a DeployKey bypass in `always` mode. Do not assume ASIG necessarily bypasses AURA-ADM; investigate its exact scope.

Open [Issue #8](https://github.com/vaidt/Projekt-Aura-BETA-/issues/8) records the controlled spoofing test: a PR-controlled workflow emitted the same three check names using the same GitHub Actions App ID. Two synthetic checks passed while the strict M1 signature gate failed and blocked merge. Thus check name + App ID alone does not bind a result to an approved workflow revision or verifier source. The issue remains open; trusted publisher/provenance and a controlled negative test are still required.

The private Bootstrap-Control repo's branch-ruleset enforcement was previously blocked by GitHub's plan-level 403. Bootstrap remains paused pending an independently controlled trust path. No rulesets were changed in this session.

## 7. Current gate disposition and next actions

| Gate | Current disposition |
|---|---|
| JCS six-vector isolated adapter comparison | PASS — exact source pins and artifact verified |
| Full RFC 8785 / production RI-PY | Not established |
| C6 / BC-02.1 | BLOCKED |
| RI-RS exact-byte preservation | Candidate added; full run incomplete; prior root cause not proven |
| Guard #13 | Draft, no independent review; resolves three advisories, not crypto-bigint |
| Core #6 | Seven checks pass on exact head; no independent review |
| Main protection in Spec/Guard/Core | Not established; endpoint reports branch unprotected |
| Issue #8 source-bound required checks | OPEN; spoofing risk demonstrated, not remediated |
| DQ-006 | OPEN |
| CONF-003 | PARTIAL / OPEN in the respective governance and Draft Conformance records |
| M1 | BLOCKED / NOT PROVEN |
| G0 / G1 | NOT PROVEN / BLOCKED |
| P-008 | CONFLICTED / NOT ESTABLISHED |
| Bootstrap | Paused; no dispatch |

Next executable sequence:
1. Obtain a complete run for PR #21; inspect `preservation-diagnostics.json` and strict parser result. If job hangs or artifact remains absent, investigate the CANONICAL-003/test step before changing the preservation parser.
2. Resolve dependency audit findings including `crypto-bigint 0.5.5` with a separate pinned, reviewed dependency change; do not relax audit/deny.
3. Resolve existing rustfmt debt in a separate, narrow change; rerun all gates on exact candidate SHA.
4. Obtain independent reviews for PR #13 and PR #6, verify effective main protection, then make separately authorized merge decisions and rerun checks on the resulting main SHAs.
5. Close Issue #8 only after the verifier source is genuinely bound and the controlled spoof test cannot satisfy trusted checks.
6. Resume full C6 only after exact-byte preservation completes and all receiver, corpus, source-pin, Merkle, negative-test and review gates are satisfied.

**Exit rule:** A scoped workflow pass is scoped technical evidence. No state moves by inference; only complete and independently reviewed technical evidence supports a technical gate, and only the proper governance process can establish normative, authority, authorization or release effect.
