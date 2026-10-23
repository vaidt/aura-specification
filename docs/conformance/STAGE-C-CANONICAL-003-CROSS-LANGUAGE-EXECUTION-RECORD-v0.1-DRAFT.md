# AURA Stage C — CANONICAL-003 cross-language execution record v0.1

**Status:** DRAFT · NON-NORMATIVE · NOT RATIFIED  
**Execution date:** 2026-10-23  
**Normative effect:** NONE  
**Release effect:** NONE  
**Coverage:** One discriminator vector only

## 1. Result

The isolated Stage C adapters and the RI-PY implementation-boundary check executed successfully against the CANONICAL-003 expected JCS bytes.

- [RI-PY production-path + RI-PY/Rust shim comparison, run 40010101982](https://github.com/vaidt/aura-specification/actions/runs/40010101982): SUCCESS.
- [Standalone Python/Rust shim comparison, run 40009604197](https://github.com/vaidt/aura-specification/actions/runs/40009604197): SUCCESS.
- [Standalone Rust probe on current adapter revision, run 40009775942](https://github.com/vaidt/aura-guard-v1.3/actions/runs/40009775942): SUCCESS.
- [Semgrep on current Rust adapter revision, run 40009775688](https://github.com/vaidt/aura-guard-v1.3/actions/runs/40009775688): SUCCESS.

The comparison workflow separately:
1. ran the actual RI-PY CANONICAL-003 implementation-boundary test, which binds `core/merkle.py::MerkleAttestor.generate_leaf` to the independently computed RFC 6962 leaf digest;
2. invoked the Stage C Python JCS shim through the common request/response contract;
3. invoked the separately developed Rust JCS shim through the same external contract;
4. compared all three emitted raw canonical byte files with the committed expected JCS file.

## 2. Pinned implementation identities

| Component | Repository / revision | JCS engine or entry point |
|---|---|---|
| Specification and test corpus | `vaidt/aura-specification` @ `758efb5fc9825281282b2ea27dd978cbbddb4cc4` | CANONICAL-003 expected oracle |
| RI-PY implementation | `vaidt/aura-poc-a-core-v3.3` @ `0a8a48cc4917c5d43ecad52de6b09abb53874684` | `core/merkle.py::MerkleAttestor.generate_leaf`; `rfc8785==0.1.4` |
| Stage C Python shim | `vaidt/aura-specification` @ `758efb5fc9825281282b2ea27dd978cbbddb4cc4` | `STAGE-C-PYTHON-JCS-PROBE`; `rfc8785==0.1.4` |
| Stage C Rust shim | `vaidt/aura-guard-v1.3` @ `e5188f6438327ec89d9f8e36396ab8e011205475` | `STAGE-C-RUST-JCS-PROBE`; `serde_json_canonicalizer==0.3.2` |

The Rust shim is a separate Cargo example target using the existing pinned dev-dependency. It does not import or alter `src/` or the production serializer/Merkle code.

## 3. Canonical byte results

| Measurement | Observed value |
|---|---|
| CANONICAL-003 input SHA-256 | `1cde8282d6df99defc16b8652cb0f43a8f327c35b8f356a8612b835ed996ec73` |
| Output length | `577` octets |
| Output trailing LF | No |
| Expected and RI-PY production output | Byte-identical |
| Expected and Python shim output | Byte-identical |
| Expected and Rust shim output | Byte-identical |
| Canonical SHA-256 | `9fb648c388c4485575d25c1d6171ba691fec51c1b433b11f4d61197bbe2a5509` |
| SHA-256(`0x00 || canonical_bytes`) | `38672ea2bd0ea87b2446efce8d4ba4adeb822e0baaecee4a54b73179198d2b3e` |
| RI-PY production method binding | `true` |

This establishes byte equality for this vector and observed engine revisions. It does not establish complete RFC 8785 coverage, full Merkle-tree conformance, or cross-platform reproducibility.

## 4. Evidence artifact

Combined run output: [artifact 12525871945 — stage-c-ri-py-ri-rs-jcs](https://github.com/vaidt/aura-specification/actions/runs/40010101982/artifacts/12525871945)

- ZIP size: 7,908 bytes.
- SHA-256 of uploaded ZIP: `c810d40845752215776419dcb5d8c81f4e47e864fa863c214669c5efc4e72da0`.
- Includes request/response envelopes, Python shim bytes, Rust shim bytes, RI-PY raw canonical output, RI-PY machine report, and a combined comparison report.

### Provenance note

The RI-PY script's internal field `core_source_commit` is populated from the workflow's `GITHUB_SHA` context and differs from the actual secondary checkout identity. The comparison report independently binds the actual RI-PY checkout using `git rev-parse HEAD` and records the pinned commit shown in Section 2. For checkout provenance, rely on that explicit checkout identity rather than the script's inherited `GITHUB_SHA` field.

## 5. Failures and correction history

The initial Rust standalone workflow's independent leaf-check step failed because the test script hashed a double-escaped textual prefix rather than the raw zero octet. The JCS bytes themselves matched the oracle. The check was corrected to construct the prefix using `bytes([0])`; the subsequent Rust-only and cross-language runs passed.

A workflow file was briefly created on `main` by a contents update targeting the wrong ref. It was removed in commit `11e512365957cd1367062e379bcd655d24048d96`. The resulting `main` tree has the same tree SHA as the pre-experiment baseline commit `991274eed57d5b3308b0607feeb4d01e6a485974` (`a7a16c6b2e3a1b79bf1678649affcb6cddf3b1ad)); comparison reports zero changed files. All continuing Stage C changes remain in Draft PRs and their isolated branches.

## 6. Gate boundary — still open

This record is a technical observation, not a normative decision.

- No full 10-stage Stage C run is claimed.
- Merkle tests are limited to the canonical leaf preimage and expected digest; full tree shape, odd-leaf behavior, proofs, domain-separation negative controls, and tamper tests remain to be executed in the next phase.
- DQ-002 and DQ-006 remain open; this record does not ratify a normative hash or serialization profile.
- F-02 and F-04 remain `OPEN`.
- `ci_execution_wired` remains `false`.
- AURA release remains `NO-GO`.


## 7. Follow-up revision and broader repository CI

After the first successful run, two formatting-only commits were made to the Rust shim. The first follow-up (`0bee5d9ca35c90d013509b52808917a6cdce9c30`) exposed remaining `rustfmt` differences; the final formatting-only revision is `31a7eeab861094fbecc82e8a61351fac49dffe43`.

The final revision passed:
- dedicated JCS probe [run #40011027689](https://github.com/vaidt/aura-guard-v1.3/actions/runs/40011027689): SUCCESS;
- `rustfmt`, `clippy`, Semgrep and the Rust-specific/hash-domain checks in the wider CI for this branch;
- the repeated production-path and common-contract comparison recorded in Section 8 below.

The broad Aura-Guard CI continues to fail `cargo-deny` and `cargo-audit` on the existing locked dependency graph. It flags:
- `RUSTSEC-2026-0381`: `webpki-roots 1.0.7`;
- `RUSTSEC-2026-0382`: `rustls-webpki 0.103.15`;
- `RUSTSEC-2026-0386`: `tokio 1.52.3`.

These dependency findings were not suppressed or fixed as part of the Stage C probe work. They remain a separate repository security-review blocker before the wider Aura-Guard PR can be considered fully green. The JCS probe's success must not be read as a pass of those dependency/security gates.

## 8. Repeat comparison on the rustfmt-clean Rust revision

A repeat of the production-path comparison executed against the latest formatted Rust shim revision:

- Workflow: [run #40011246139](https://github.com/vaidt/aura-specification/actions/runs/40011246139) — **SUCCESS**.
- Workflow commit containing the updated pin and orchestrator: `vaidt/aura-specification@d8b03a80eb1bcae2ffab99136eae3c571cc8fa30`.
- Rust shim source: `vaidt/aura-guard-v1.3@31a7eeab861094fbecc82e8a61351fac49dffe43`.
- The Rust adapter contract/oracle suite again passed **6/6** tests; the Python contract suite passed **8/8** tests.
- RI-PY CANONICAL-003 implementation-boundary report again returned `result=PASS` with `core_method_binding=true`.
- The actual RI-PY implementation checkout was `vaidt/aura-poc-a-core-v3.3@0a8a48cc4917c5d43ecad52de6b09abb53874684`.
- RI-PY production output, Python shim output, Rust shim output, and the committed expected JCS oracle were byte-identical: **577 octets**, no final LF.
- Canonical SHA-256 remained `9fb648c388c4485575d25c1d6171ba691fec51c1b433b11f4d61197bbe2a5509`.
- Probe-only leaf digest remained `38672ea2bd0ea87b2446efce8d4ba4adeb822e0baaecee4a54b73179198d2b3e`.

New combined evidence: [artifact 12525867966 — stage-c-ri-py-ri-rs-jcs](https://github.com/vaidt/aura-specification/actions/runs/40011246139/artifacts/12525867966).

- ZIP size: 7,903 bytes.
- ZIP SHA-256: `49e8716ea91a567f42cbb4c6915eabd4f745b427fb22cf0c52e79106b6b21940`.

The inherited `core_source_commit` metadata note in Section 4 still applies: the separately checked-out RI-PY commit identity in the combined report is more reliable than the raw script's inherited `GITHUB_SHA` field.

This repeat addresses only the Rust source formatting revision and confirms no change to the CANONICAL-003 technical result. It still covers one vector, not a complete RFC 8785 corpus or full Merkle-tree/proof/negative-test suite.
