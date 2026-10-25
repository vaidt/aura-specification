# AURA — DQ-006 / CONF-003 / C6 Residual Gap Register

**Document ID:** AURA-GAP-DQ006-CONF003-C6-v1.0-DRAFT  
**Assessment date:** 2026-10-25  
**Classification:** Engineering evidence / gap analysis  
**Status:** DRAFT — NON-CONSTITUTIVE — NOT A RATIFICATION RECORD  
**Baseline:** vaid t/aura-specification/main @ 11e512365957cd1367062e379bcd655d24048d96

## 1. Executive decision

The evidence supports a bounded technical PASS for the 27-case BC-02.1 receipt-wire corpus, not full AURA conformance or release readiness.

| Work item | Current observed state | Disposition |
|---|---|---|
| Core PR #8 | OPEN / DRAFT; refreshed head fe3be05794d3f254d98af1464e598e5b9be2e369; run #40175595587 SUCCESS | Preserve result; independent review remains absent |
| C6 integration PR #45 | OPEN / DRAFT; head 38821305ddb93eca96d9eb86e53d5c2db5d91295; run #40176350679 SUCCESS | Preserve as bounded technical evidence; independent review remains absent |
| Integrated C6 | RI-PY 27/27 and RI-RS 27/27 on x86_64 and aarch64; per-case results agree | PASS only for the pinned corpus, implementations and source revisions |
| C6 gate field | BLOCKED_PENDING_EVIDENCE_REVIEW | Do not manually overwrite |
| CONF-003 | PARTIAL in the current conformance record | Remains PARTIAL |
| DQ-006 | OPEN in the authoritative closure package | Remains OPEN |
| M1 / G1 | BLOCKED / NOT PROVEN per current project operating instruction | No change |
| Release | NO-GO pending security, conformance and governance gates | No change |

Three contracts must not be conflated:

1. **BC-02.1 C6 strict-wire consumption:** parsing the receipt envelope and checking structure, provenance fields, Base64 octets, length and digest.
2. **CONF-003 / DQ-006 canonicalization:** RFC 8785 canonical bytes, SHA-256 digest and RFC 6962 leaf domain, plus prohibited-input controls, source-of-record and closure requirements.
3. **Constant-time cryptographic assurance:** bounded evidence for crypto-bigint/ECC and its analysis harness. A strict-wire PASS is not evidence that cryptographic operations are constant-time.

## 2. Evidence baseline and provenance

### 2.1 Core PR #8

- PR: https://github.com/vaidt/aura-poc-a-core-v3.3/pull/8
- Exact refreshed head: fe3be05794d3f254d98af1464e598e5b9be2e369
- Core main incorporated: 6e739116f30608f7fadec1578cefc798d2b1480c
- Fresh run: https://github.com/vaidt/aura-poc-a-core-v3.3/actions/runs/40175595587
- Observed result: 174 passed, 8 warnings, 17 subtests passed; x86_64, aarch64, WASM compatibility and cross-platform determinism jobs passed.
- The log records installation of rfc8785==0.1.4 before test execution.
- PR status at assessment: OPEN / DRAFT / NOT MERGED; formal review list empty.

The missing test dependency is resolved for this exact candidate. This does not constitute approval of the parser contract or authority to merge.

### 2.2 Integrated C6 PR #45

- PR: https://github.com/vaidt/aura-specification/pull/45
- Exact integration harness commit: 38821305ddb93eca96d9eb86e53d5c2db5d91295
- Integrated run: https://github.com/vaidt/aura-specification/actions/runs/40176350679
- Exact Core source: fe3be05794d3f254d98af1464e598e5b9be2e369
- Exact RI-RS source: feab2d9c369cd5f8cbabe10d713d278b0b09da8b
- Exact C6 manifest/materializer source: 6b4f3dcc46841bb17fafa3e1b1cc8ea9c0397330
- Shared materialized index SHA-256: 445d5808cb76a24b916a91e91636d4ce10ac3b0239f9eb2f474264783bc41181
- RI-PY result report SHA-256: cfdbd0fbbc1442bba0b7a70a5bf7c76fc5ecd9cb2dabe27ffe4379053196a6a4
- RI-RS result report SHA-256: b289367fc2e19f0666d202d35eb257d795ff18c589d7d0323c202e6a4636e25b
- Cross-implementation summary ZIP SHA-256: ad78a4eccaa7e4c467a4a65e483e426e1042fd5411ce9de036ad75a82b9307f4
- x86_64 bundle ZIP SHA-256: ffbf20cb99341bcd6c7cd33c08077ccaef0be10874e912116580b7499c6d9a4b
- aarch64 bundle ZIP SHA-256: 77ab20466221e078ff6bcef2f6f9a0795f4b2cfdd5f3e0843d6f1fe5702feba3

Observed result:
- RI-PY: 27/27 matched on x86_64 and 27/27 on aarch64.
- RI-RS: 27/27 matched on x86_64 and 27/27 on aarch64.
- Per-case result and rejection code agree between implementations.
- Each implementation's report and the corpus index are byte-identical across architectures.
- RI-RS preservation validator rejects all 9 negative evidence fixtures as intended.
- The integrated run reports result=PASS, mismatches=[], and c6_gate_status=BLOCKED_PENDING_EVIDENCE_REVIEW.
- PR status at assessment: OPEN / DRAFT / NOT MERGED; formal review list empty.

The initial integration attempt failed because the verifier incorrectly demanded governance-effect fields in an RI-RS diagnostics document whose schema does not define them. The verifier was corrected; the later run on the exact final commit passed all three workflow jobs. The correction is retained in the record.

## 3. Evidence review: action and guardrails

### 3.1 Do not mutate the generated gate field

These fields mean different things:

- result=PASS: the workflow passed for the pinned technical test contract.
- c6_gate_status=BLOCKED_PENDING_EVIDENCE_REVIEW: the evidence package still awaits independent review.
- governance_effect=NONE, authorization_effect=NONE and release_effect=NONE: the technical run has no constitutive effect.

A reviewer must not change c6_gate_status by editing the JSON artifact in place. That would detach the reviewed decision from the generated result and its digest. The review outcome should instead be a separate review-decision record referencing the exact run, source commits, artifact IDs, digests, reviewer authority basis, scope, exceptions and rationale.

A later approved gate transition, if authorized, must be executed through the controlled status procedure and recorded as a new event. The original CI artifact remains unchanged.

### 3.2 Independent review packet checklist

The packet should contain:
1. Both architecture evidence ZIPs and cross-implementation summary JSON/ZIP.
2. Exact source commits, Git blob OIDs and content SHA-256 bindings.
3. Workflow run #40176350679, PR #45 head, Core PR #8 and run #40175595587.
4. Verification that all 27 inputs exist and their lengths/digests match the shared index.
5. Per-case RI-PY/RI-RS comparison, report digests and byte-identical architecture comparison.
6. The failed-first-run/correction record and exact verifier/harness version that passed.
7. A limitation statement: bounded BC-02.1 evidence, not full CONF-003, DQ-006 closure, general constant-time proof, protocol ratification or release authorization.
8. Verified reviewer identity/competence basis and a separate controlled disposition record.

The existence, membership or authority of an audit committee is not established here. The project owner must identify the competent reviewer/body and provide the applicable authority record before a review can have governance effect.

## 4. Existing C6 corpus coverage

The present corpus is explicitly DRAFT_NON_NORMATIVE / C6_PREPARATION. It contains 27 cases: 2 positive cases and 25 negative mutations.

| Dimension | Existing coverage |
|---|---|
| Positive receipts | Non-UTF-8 raw artifact octets transported through Base64; empty raw-octet sequence |
| Object shape | Unknown top-level and nested fields; one missing top-level field |
| Required values/types | Null string; boolean masquerading as integer; fractional and negative octet length; JSON array instead of Base64 string |
| Schema identity | Wrong schema identifier and unsupported schema version |
| Base64 | Invalid alphabet; missing padding/non-canonical encoding |
| Byte integrity | Octet-length mismatch; digest mismatch |
| JSON envelope | Duplicate top-level key; duplicate nested key; malformed JSON; invalid UTF-8 |
| Result-authority firewall | Prohibited values PASS and CONFORMANT in two semantic/provenance locations |
| Identity separation | Receiver/implementation alias; adapter/implementation alias |
| Evidence preservation | 9 negative validator fixtures: wrong index digest, count mismatch, duplicate/missing IDs, unmatched rows, wrong ID set, malformed JSON, concatenated JSON and trailing data |
| Source provenance | Exact commits, blob OIDs and content SHA-256 for consumers, harness, manifest and materializer |

This is useful targeted coverage, not exhaustive parser robustness, every-field type coverage, configured size/nesting limits, or a protocol-wide approved receipt contract.

## 5. Candidate C6 expansion — 50 additional vectors for triage

This is a planning inventory, not an approved normative vector set. The 50 cases should be reviewed against the controlling receipt contract and error taxonomy. Where the expected behavior is not established by the contract, mark the case CONTRACT_DECISION_REQUIRED rather than inventing an expected result.

| Proposed ID range | Count | Candidate dimension |
|---|---:|---|
| C6-X-001…012 | 12 | Missing each nested object; unknown property in each nested object; root scalar/array shape variants in the test matrix |
| C6-X-013…020 | 8 | JSON transport edge cases: BOM handling, trailing garbage, concatenated documents, escaped-equivalent duplicate keys at two depths, non-standard numeric constants and top-level scalar/array cases |
| C6-X-021…028 | 8 | Base64: URL-safe alphabet, embedded whitespace, excess padding, invalid pad bits, non-ASCII input, line breaks, canonical re-encoding, full 0x00–0xFF octet round-trip |
| C6-X-029…035 | 7 | Numeric boundaries: null octet length, string type, exponent-notation integer-looking token, zero/negative-zero lexical behavior, maximum accepted length, over-range integer and very large signed integer |
| C6-X-036…041 | 6 | Digest controls: uppercase hex, non-hex character, 63/65-character digest, digest over encoded Base64 text instead of decoded bytes, one-octet source mutation |
| C6-X-042…046 | 5 | Provenance: blank required fields by identity object, receiver/adapter alias, malformed source-commit format if contract requires SHA, prohibited-result values in additional semantic fields |
| C6-X-047…050 | 4 | Error precedence for multi-defect inputs, configured size limit, configured nesting limit, bounded mutation/property-based fuzz seed set with crash/differential checks |
| **Total candidate additions** | **50** | Planning estimate; final count depends on contract decisions and deduplication |

Each accepted vector must bind stable ID, corpus version, requirement/invariant/CONF reference, exact input bytes/length/SHA-256, expected class and error code with its normative basis, exact RI-PY and RI-RS outcomes, independent comparison, source commit/blob, runtime/toolchain/platform, and classification as normative/draft/contract-dependent.

## 6. CONF-003 / DQ-006 residuals — separate canonicalization workstream

The C6 receipt-parser result does not discharge CONF-003. The controlling requirement is the current CONF-003 document (DRAFT/PARTIAL) and DQ-006 closure record.

| Item | Current state in controlling records | Required next act |
|---|---|---|
| JCS profile, canonical SHA-256 and RFC 6962 leaf domain | Contract described in APS-200 §8 and APS-300 §5; draft status remains | Do not infer normative approval from implementation tests |
| CANONICAL-003 discriminator | Technical PASS for the tested vector in vaid t/* working repositories | Preserve as finite evidence; not exhaustive RFC 8785 proof |
| CONF-003 C1–C8 and N1–N3 | Reported PASS for existing cross-language evidence | Bind exact evidence files and gate version in review packet |
| CONF-003 §4.5 prohibited-input controls | NOT EXECUTED in the current CONF-003 status table | Add and run controlled inputs for the four classes below |
| DQ6-R2: authoritative RI-RS boundary | OPEN | Select one source-of-record path and dispose of competing implementations/dependency placement |
| DQ6-R3: evidence reachability | OPEN against the currently named Aura-IDToken repositories | Publish evidence there or formally accept an immutable alternative route |
| DQ6-R4: ratification | OPEN / NOT PERFORMED | Competent authority reviews package after R1–R3 |
| Production compatibility | Open release-control residual | Review profile/version boundary and historical-evidence impact of the RI-PY production hash/Merkle change |

### 6.1 Prohibited-input controls required by APS-200 §8.4

CONF-003 must reject/refuse to digest these prohibited substitutes for canonical bytes:

1. Pretty-printed or implementation-formatted JSON.
2. Alternate object serializations that are not the approved canonical bytes.
3. Escaped, Base64 or hexadecimal encodings of canonical bytes passed as the digest input.
4. A hexadecimal digest string where raw digest bytes are required.

These are not the same as C6 Base64 transport tests or the older C1–C8/N1–N3 controls. They need their own defined boundary, expected rejection, gate logs, corpus-digest verification after temporary mutation and independent review.

### 6.2 Candidate JCS edge-vector inventory

Prioritize:
- ES6 number cases: -0, integral floats, exponent thresholds and binary64 boundary/rounding cases.
- Non-finite numeric inputs: NaN, positive Infinity and negative Infinity, with explicit expected rejection at the approved boundary.
- UTF-16 property ordering that distinguishes UTF-16 code-unit order from Unicode scalar-value or UTF-8 byte order.
- Unicode escaping, raw UTF-8 output, control characters, supplementary characters, lone surrogate handling and an explicit decision on normalization.
- Empty object/array, nested arrays/objects and representative payload-size boundaries.
- Canonical-byte/digest/leaf mutation controls, including incorrect 0x01 leaf domain and textual “0x00” instead of a raw octet.
- The prohibited-input cases in §6.1, separately from parser transport encoding.
- Exact per-side engine identity/version, adapter digest, source commit, clean-worktree state, toolchain/platform, raw canonical bytes and independently recomputed digest/leaf.

CANONICAL-003 already exercises several discriminator classes. These candidates improve edge coverage; they are not claims that the existing fixture failed.

## 7. Constant-time evidence workstream — crypto-bigint / ECC

This workstream is separate from C6 strict-wire parsing and CONF-003 JCS serialization.

### 7.1 Current observed status

- Aura-Guard main at e0ed7a8b381b725fe65bd86716894bfdf17d3a94 retains crypto-bigint 0.5.5 in the existing dependency graph.
- PR #25 is OPEN / DRAFT at f94e269e5a2098ef374dcfb7dc8ceef09d08c4ed; its stacked candidate uses crypto-bigint 0.7.7 and earlier Standard CI/BINSEC runs reported SUCCESS.
- The latest strengthened coverage-detection run #40141221070 is on the separate ops/binsec-fix-test branch at bf0ee5ec…, using pinned upstream crypto-bigint source f17d82ad… and cargo-checkct source 85271e5c…. It is not the PR #25 head.
- The hardened harness showed eight target/driver combinations and fail-closed handling of incomplete coverage on that experimental source branch. This does not prove all Aura-Guard execution paths constant-time.
- The ECC migration changes observable high-S signature acceptance. This remains a protocol/compatibility decision, not a CI verdict.

### 7.2 Required constant-time evidence pack

| ID | Requirement | Required evidence |
|---|---|---|
| CT-01 | Exact source/dependency identity | PR #25 head, Cargo.lock package, registry checksum, upstream commit/tree/file hashes, Rust toolchain and compiler flags |
| CT-02 | Complete analysis coverage | All target/driver pairs enumerated before execution; panic sentinel on every binary; exact matrix recorded |
| CT-03 | Analyzer outcome integrity | Per-binary BINSEC reports; control-flow and memory-access results; no unknown/insecure result, parse failure, dropped report or incomplete-coverage warning accepted as success |
| CT-04 | Fail-closed negative controls | Missing sentinel, missing target/driver, unknown result, malformed report, coverage warning and incomplete artifact inventory each force failure |
| CT-05 | Exact-head replay | Run hardened harness with exact PR #25 candidate and pinned upstream/tool sources; record source SHA and job IDs in one manifest |
| CT-06 | Application-path review | Establish which secret-dependent operations the ECC verifier invokes; assess relevant call paths, not only the upstream crate in isolation |
| CT-07 | Functional crypto regression | Wycheproof ECDSA corpus, high-S/low-S cases, malformed signatures, negative tests and compatibility results |
| CT-08 | Dependency/security gate | cargo-audit, cargo-deny, lockfile review, SBOM and remaining RustSec advisories on exact candidate |
| CT-09 | Independent cryptographic review | Review harness overlay, analyzer settings, source coverage, limitations and high-S semantic change |
| CT-10 | Final interpretation | Separate narrow BINSEC result from general constant-time claims; document limitations and residual risk |

Remaining work includes demonstrating that the strengthened coverage-warning negative test fails for intentionally incomplete analysis; rerunning the hardened harness on the exact PR #25 head; retaining hashed runtime overlays and all eight binary/report digests; reviewing the application verifier call path; and recording an explicit high-S/low-S disposition. Do not claim Aura-Guard main is remediated until the dependency fix is integrated through an authorized path with required review.

## 8. Governance firewall and merge recommendation

### 8.1 Preserve current state

- PR #8 — OPEN / DRAFT / NOT MERGED.
- PR #45 — OPEN / DRAFT / NOT MERGED.
- c6_gate_status — BLOCKED_PENDING_EVIDENCE_REVIEW.
- CONF-003 — PARTIAL.
- DQ-006 — OPEN.
- M1/G1 — remain BLOCKED / NOT PROVEN under the current project operating instruction.
- Release — NO-GO.

Reasons:
1. Neither PR #8 nor PR #45 has a formal review submission at this assessment.
2. PR #45 adds an experimental evidence workflow, runner and verifier; their successful execution is evidence, not independent review of the tools.
3. DQ-006 still has R2/R3/R4 open and a production compatibility residual.
4. Repository governance materials conflict: the M1 closure record is preceded by a notice stating that its deprecation annotation is non-constitutive and authority continuity needs competent ratification, registration and independent verification, while the body still claims executed closure. This conflict requires competent evidence review; this register does not decide it.
5. A green test result does not self-authorize removal of Draft, merge, ratification or release.

### 8.2 Minimum review-decision fields

A controlled review record should include decision ID; competent review body/role; verified reviewer identity and authority basis; source run IDs; PR heads; corpus/index digest; architecture artifact IDs/digests; criteria passed/failed; exceptions/limitations; disposition (ACCEPT_TECHNICAL_EVIDENCE, RETURN_FOR_REMEDIATION or INSUFFICIENT_EVIDENCE); rationale; signature/attestation; timestamp; scope; and explicit governance/authorization/release effects.

Do not encode reviewer approval by editing the generated C6 JSON. Record it separately and then follow the authorized status-transition procedure. This register does not identify a committee recipient or assert that committee authority has been verified.

## 9. Execution order

1. **Independent evidence review:** deliver immutable C6 packages and the Core run to the named competent reviewer; preserve hashes and the first-run/correction record.
2. **Independent code review:** review PR #8 parser/tests and PR #45 runner/verifier/workflow. Address the eight non-blocking Core pytest warnings in a separate scoped change if maintainers agree.
3. **C6 vector expansion:** decide contract-dependent boundaries, then version the draft corpus extension. Re-run both consumers and full integrity/architecture comparison.
4. **CONF-003 closure:** execute prohibited-input controls, preserve complete EVID-CORE evidence, reconcile RI-RS source-of-record/reachability, and review production profile/historical-evidence compatibility.
5. **Constant-time closure:** run the hardened harness on exact PR #25 head, complete independent cryptographic review and high-S/low-S disposition, and preserve all negative controls.
6. **Governance review:** only after applicable technical residuals and source-of-record conflicts are resolved may the competent authority decide governance status through a separate recorded act.
7. **Merge/release:** only after required reviews and authorization are evidenced.

## 10. Final disposition

This is a planning/evidence-gap artifact only. It adds no normative rule, does not rewrite historical evidence, does not change a gate field, does not ratify DQ-006 or CONF-003, does not prove M1/G1 authority continuity, and does not authorize a merge or release.

**Conclusion:** C6 is technically PASS for its pinned 27-case BC-02.1 corpus on the two named architectures. The C6 gate still awaits evidence review. CONF-003 remains PARTIAL, DQ-006 remains OPEN, constant-time assurance remains a separate bounded evidence task, and M1/G1 remain blocked pending the required competent-authority process.
