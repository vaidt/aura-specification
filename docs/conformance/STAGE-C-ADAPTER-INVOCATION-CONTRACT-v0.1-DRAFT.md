# Stage C — Adapter Invocation Contract v0.1 (Draft)

**Status:** DRAFT · NON-NORMATIVE · NOT RATIFIED  
**Execution status:** CONTRACT REVIEW ONLY — NO STAGE C RUN CLAIMED  
**Protocol effect:** NONE  
**Governance effect:** NONE  
**Target:** Isolated Stage C engineering branch only

## 1. Purpose and hard boundary

This note records the first interface audit and proposes a stable orchestration boundary for the isolated RI-PY and RI-RS work. It does not alter either reference implementation, freeze a canonicalization profile, ratify DQ-006/DQ-002, or authorize a conformance decision.

The audit found two different adapter classes that must not be conflated:

1. **JCS execution adapter:** transforms a parsed JSON value into RFC 8785 canonical UTF-8 bytes.
2. **BC-02 receiver adapter:** accepts an already-issued sequence of octets and emits a BC-02.1 receipt describing the received material.

A receiver receipt is not a JCS result; JCS output equality is not a receiver receipt; neither artifact by itself determines protocol conformance.

## 2. Reviewed source snapshot

Review baseline for this note:

- Specification repository: `vaidt/aura-specification`, base commit `991274eed57d5b3308b0607feeb4d01e6a485974`.
- RI-PY source repository: `Aura-IDToken/aura-poc-a-core-v3.3`, default-branch commit `43f054f8deb7c9644c52148d6496b493512d32b0`.
- RI-RS source repository: `Aura-IDToken/aura-guard-v1.3`, default-branch commit `89447ce12b1aecca4048f848a05a5c0c81f33b24`.

Relevant source references:

- RI-PY receiver CLI: `conformance/boundary/ri_py_adapter.py`; blob `40f073b40f3c651f46a80eb3b269b934c9097336`.
- RI-PY receiver: `conformance/boundary/ri_py_receiver.py`; blob `708cc01b1f74080f3cf0f95e1b402851cdd77178`.
- RI-RS JCS function adapter: `conformance/canonical/jcs.rs`; blob `a3abf66717020ed7a13902f21585668e51ec23ec`.
- RI-RS canonical probe: `conformance/canonical/canonical_001.rs`; blob `d59068d1f871febe53a40d59c92d2320783790b8`.
- Specification-side RI-RS receipt receiver: `conformance/boundary/ri_rs_receiver.rs`; blob `b2117f295902ae966e27ef99da8c574f057a7338`.
- Specification-side RI-RS P-01 wrapper: `conformance/boundary/ri-rs/src/bin/p01_handoff.rs`; blob `1f963d7b3dc25462f81073fc08bff372fa99202d`.
- Shared receipt contract: `conformance/boundary/BC-02.1-COMMON-RECEIPT-SCHEMA-v1.md`; blob `f40f7a2ea246f382d12490a6489159f9e226fd17`.

These references are observations of the reviewed public tree, not assertions that those commits were executed in this review.

## 3. Findings: current invocation is not uniform

### 3.1 BC-02.2 RI-PY receiver adapter

Current invocation shape:

```text
python3 -m conformance.boundary.ri_py_adapter <artifact-path> \
  --fixture-id <id> \
  --fixture-artifact-identity <identity> \
  --source-commit <commit> \
  --method <method> \
  --environment-id <environment> \
  --receipt-out <receipt-path>
```

The artifact is opened in binary mode. The adapter prints human-readable intake/report text plus a serialized receipt; receipt-file output is optional. The receiver computes SHA-256 from the octets it actually receives. The receiver's construction and schema validation are explicitly not conformance evaluation.

### 3.2 BC-02.3 RI-RS receipt adapter

Current invocation shape in the specification workspace:

```text
cargo run --bin p01_handoff -- <artifact-path> <receipt-out-path>
```

Provenance and fixture metadata are supplied through environment variables, some of which currently default to `UNSET`. The binary prints validation lines and writes its receipt. The low-level Rust receiver is a free function taking positional values, unlike the RI-PY receiver instance method.

### 3.3 JCS execution surfaces

RI-RS has a dedicated JCS function with the narrow transformation `serde_json::Value -> Vec<u8>`, exercised by `cargo test --test canonical_001`. It is a library/test surface, not a common standalone adapter CLI, and is explicitly outside the production runtime.

The reviewed RI-PY default-branch tree does not expose an equivalent RFC 8785 JCS function/CLI. Its `ri_py_adapter.py` is the BC-02 receiver adapter, not a JCS canonicalizer; its default-branch `pyproject.toml` does not pin or declare a JCS runtime dependency. Consequently, **the existing RI-PY receiver must not be presented as an executable JCS adapter**. A separate, pinned experimental JCS adapter is required before a genuine Stage C cross-language JCS run can be claimed.

### 3.4 Previous handoff evidence

`conformance/boundary/CONTROLLED-P01-HANDOFF-RECORD.md` documents an earlier RI-PY/RI-RS receipt handoff. That is useful evidence for raw-octet transfer and receipt comparison; it does not substitute for a new JCS-discriminator execution, Merkle test run, or present-day reproducibility check.

## 4. Proposed outer invocation contract

The runner should adapt native interfaces through thin, separately versioned shims. It should not rewrite frozen source implementations or infer results from mixed human-readable logs.

### 4.1 Common runner request

Each operation receives one UTF-8 JSON request file conforming to `AURA-STAGE-C-ADAPTER-REQUEST/0.1`:

```json
{
  "schema": "AURA-STAGE-C-ADAPTER-REQUEST/0.1",
  "run_id": "generated-by-runner",
  "operation": "jcs.canonicalize",
  "fixture_id": "CANONICAL-003",
  "input_path": "fixtures/corpus/CANONICAL-003_jcs_full_discriminator.json",
  "expected_path": "fixtures/corpus/CANONICAL-003_jcs_full_discriminator.expected.jcs",
  "expected_sha256": "runner-computed-from-committed-file",
  "source_commit": "exact-40-character-commit"
}
```

The example illustrates field shape only. The runner MUST compute the actual expected-file digest at runtime; it MUST NOT copy the placeholder text above into a real request.

### 4.2 Common output boundary

Each shim writes a machine-readable response JSON file and raw output octets to separate files. Stdout/stderr are captured separately as logs and never parsed as the source of cryptographic bytes.

The response envelope is `AURA-STAGE-C-ADAPTER-RESPONSE/0.1` and includes:

- `schema`, `run_id`, and `operation`;
- adapter identity, language, adapter version, exact source commit, engine name and engine version;
- input fixture identity, input octet length and SHA-256;
- output path, output octet length and SHA-256;
- `execution_status` from the closed operational set `COMPLETED | INPUT_ERROR | EXECUTION_ERROR | OUTPUT_ERROR`.

The envelope MUST NOT include protocol `PASS/FAIL`, `CONFORMANT/NON_CONFORMANT), acceptance state, or a ratification claim. Only the independent Stage C evaluator can compare output bytes against the expected corpus and produce a technical test report. Its report still has no normative or release authority.

### 4.3 Standard shim command

The runner invokes each thin shim using the same outer command shape:

```text
<shim> --request <request.json> --response <response.json> --output-octets <output.bin>
```

The shim may translate the request into each implementation's native invocation. No shell interpolation of request values is permitted. The runner uses a controlled working directory, a minimal environment, pinned dependencies/toolchain and explicit timeouts. Missing commit identity, failed execution, missing output, invalid JSON envelope, or hash/length mismatch is a hard stop.

Operational process exit contract:

| Exit code | Meaning |
|---:|---|
| 0 | Shim execution completed and its response envelope was written; this is not conformance PASS. |
| 2 | Request or input invalid/missing. |
| 3 | Underlying adapter/engine failed. |
| 4 | Output missing, malformed, or inconsistent with the response envelope. |
| Other non-zero | Unexpected failure; stop and preserve logs. |

A zero exit code MUST NOT be interpreted as a conformance result.

## 5. Separate rules for the two operations

### 5.1 `jcs.canonicalize`

- Input is the exact committed fixture file, read as bytes; the JSON object is parsed only inside the JCS adapter.
- Output is the exact canonical UTF-8 octet sequence, with no BOM and no trailing newline added by the shim.
- Compare raw output bytes with the committed discriminator file; semantic JSON equality is insufficient.
- Compute SHA-256 from the emitted output bytes independently in the runner.
- Do not mutate the fixture, expected JCS bytes, production serializer, or Merkle runtime.
- The Python JCS engine and Rust JCS engine must be pinned and identified separately. The selected Python engine is still unresolved in this proposal; do not label it RI-PY-native until source/reachability and ownership are evidenced.

### 5.2 `receiver.receive_octets`

- Input is an already-issued artifact read in binary mode; no parse/reserialize, normalization, newline changes, Base64-text hashing, or expected-digest injection is permitted.
- Both receivers must produce BC-02.1 receipt material; raw octets are Base64-encoded only at the JSON transport boundary.
- Normalize only the outer process interface. Preserve independently authored receipt construction, validation implementation, and provenance fields.
- Compare decoded receipt octets and receiver-derived digest, but do not treat the receipt as evidence of JCS or Merkle conformance.

## 6. Initial contract checks before implementing wrappers

The first dry-run must begin with these bounded checks, in order:

1. Record the exact source commits and file blob identities listed in Section 2.
2. Validate request/response schema and reject missing/unknown mandatory fields.
3. Confirm both receiver shims can accept the same artifact path and explicit provenance while preserving raw octets. Use only synthetic bytes for this interface smoke test.
4. Confirm deterministic receipt bytes or explicitly document and normalize only transport representation, not receipt meaning.
5. Separately prove whether a RI-PY JCS engine can be invoked in an isolated experiment. If not, stop before cross-language JCS comparison; do not silently substitute the receiver adapter.
6. Only after Sections 1–5 pass, run the discriminator corpus, then Merkle profile probes and negative controls.

No real Stage C gate is considered wired by completing this interface audit.

## 7. Isolation and non-mutation requirements

- Work only on an experimental branch and Draft PR; no merge, release, tag, protected-branch change, or auto-merge.
- Workflow permissions are read-only for repository contents. No production environment or secrets are permitted.
- No generated report is written back to `main`; upload reports only as run artifacts.
- A before/after snapshot must record `main` SHA, relevant PR states and workflow configuration. Any unexpected mutation is a failed dry-run.
- The experiment cannot change F-02/F-04, `ci_execution_wired`, governance status, DQ-002/DQ-006 disposition, or release `NO-GO`.
- Test labels `PASS/FAIL` describe only a named engineering assertion and are not a normative conformance, authorization, ratification, or release decision.

## 8. Acceptance criteria for this draft

- The invocation difference between the two existing BC-02 receiver adapters is explicitly mapped rather than hidden.
- The JCS and receiver-adapter responsibilities are kept distinct.
- The missing default-branch RI-PY JCS execution surface is recorded as a blocking dependency.
- Request/response contracts carry actual provenance and bind outputs to bytes.
- The proposal remains visibly draft, non-normative and unexecuted.

**Disposition:** Interface audit documented. The proposed outer contract is not implemented or ratified. No complete Stage C execution is claimed.
