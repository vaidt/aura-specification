# AURA C6 — Real-Flow Evidence and Gate Blockers v0.1

**Classification:** NON-NORMATIVE ENGINEERING AUDIT NOTE  
**State:** BLOCKED — NO EXECUTION AUTHORITY — NO GATE PROMOTION  
**Scope:** Existing P-01 receiver-flow evidence; BC-02 B-VAL-014; CONF-003 §4.5; preconditions and negative controls.  
**Pinned review head:** `bd0d796efc744349906377b9450c977806338bac` (`experiment/stage-c-c6-strict-wire-consumer-20261024`)  
**Authority / governance / authorization / release effect:** NONE.

This note records an independent review of existing evidence and the conditions that prevent a valid new execution. It is not a protocol result, BC-02 validation report, conformance evidence, or authorization.

## 1. Existing actual-artifact handoff evidence

A prior controlled P-01 receiver handoff is recorded on 2026-08-23. This is material evidence that both receiver paths read bytes from the named artifact at that earlier execution, but its own log and comparison explicitly state that B-VAL-014 was not executed and CONF-003 §4.5 has no result.

Issued artifact:
- Path: `conformance/boundary/p01/FIX-DIGEST-P01.canonical.json`
- Git blob: `b45ffa980a1a776b6143d7fcb255fbfa8a436582`
- Length: 15 octets; hex: `7b2261223a312c2262223a2278227d`
- SHA-256: `ecf9e98ec0641e23113ff3ce8bdc78d0ddd249886517fd4a7f68cc83d4e65667`

Evidence artifacts, pinned at the reviewed specification head:
- [Controlled P-01 handoff record](https://github.com/vaidt/aura-specification/blob/experiment/stage-c-c6-strict-wire-consumer-20261024/conformance/boundary/CONTROLLED-P01-HANDOFF-RECORD.md) — blob `fe3de6b4af0a872892cdb07b94bf0c2620c74c8f`
- [Cross-receiver comparison](https://github.com/vaidt/aura-specification/blob/experiment/stage-c-c6-strict-wire-consumer-20261024/conformance/boundary/evidence/controlled-p01-handoff/CROSS-RECEIVER-COMPARISON.txt) — blob `3bc63e8fc7c135112b66fd83db327d1733730f2a`
- RI-PY log — blob `14b1396964dcb0515c04254d13a5936d709cc4e5`; receipt — blob `7bd81f082011b8578eef5f28c1d6357c1bfa1ac1`; manifest — blob `aae58d69e97201e000514b237be6d2ee06b657d1`
- RI-RS log — blob `48ff1437b8ee1f21482285606bb00e8cb6e1d454`; receipt — blob `836cbf2170b07d5b075374b9d6a3ab6850952d53`; manifest — blob `93dfb76f0f5bd02ac072c29aa3ecdfe56193d4fe`

The record reports:
- RI-PY source checkout `d943807c359af982fd573ec4ff690b7fa265dc42`, execution time `2026-08-23T21:36:53Z`.
- RI-RS source checkout `49e848a007b18b78240100246f7cc348cf9ebd62`, execution time `2026-08-23T21:37:11Z`.
- Both receivers report 15 octets and receiver-derived SHA-256 equal to the independent issued-artifact hash. The comparison says each received octet sequence matched the issued artifact and each other.
- 24/24 recorded R-VAL checks validate receipt/schema properties only.

**Limit:** Both receiver logs explicitly end with `B-VAL-014 NOT EXECUTED`, `CONF-003 section 4.5 NO RESULT`, and `CONFORMANCE NOT DETERMINED`. These artifacts cannot be reclassified as a C6 or §4.5 result. Their timestamps/source pins are historical, not a fresh run against the current pinned experimental heads.

## 2. Controlling definition for B-VAL-014

The [B-VAL-014 definition reconciliation record](https://github.com/vaidt/aura-specification/blob/experiment/stage-c-c6-strict-wire-consumer-20261024/conformance/boundary/B-VAL-014-DEFINITION-RECONCILIATION-RECORD.md), blob `281b29ca77dded2bbeb16ecc2fe916774ac57bb6`, identifies the controlling engineering definition as BC-02 §14:

```text
receipt.receipt_digest == input_segment_sha256      on BOTH sides
receipt_digest_source  == RECEIVER_RECOMPUTED       on BOTH sides
raw_input_encoding     ∈ {identity, base64, base16}
```

The assertion is transfer evidence. It must not absorb adjacent assertions:
- B-VAL-012 is a companion: each receiver recomputes its digest over the buffer it actually received, and the two observations are compared.
- B-VAL-013 is artifact traceability, not proof of octet transfer.
- B-VAL-019 is a separate no-reconstruction invariant.

The reconciliation record marks B-VAL-014 as `NOT EXECUTED` and explicitly says it grants no execution authority. It also identifies unresolved execution preconditions, including a material schema-binding gap and BNC-1 not executed.

## 3. Blocking prerequisites before BC-02 validation

The controlling [BC-02 construction contract](https://github.com/vaidt/aura-specification/blob/e2066bd/conformance/boundary/BC-02_IMMUTABLE_FIXTURE_HANDOFF.md) §15 says validation is to occur only after §19 dependencies are discharged; it is “not authorized by this document.” It says **validation MUST NOT begin with an unmet precondition**.

| Precondition | Required evidence | Current disposition |
|---|---|---|
| VE-01 | Versioned, field-bound `CONFORMANCE_FIXTURE_REGISTRY_v1`; Registry entry resolvable | **BLOCKED** — BC-02-DEP-001 says the Registry contract cannot be resolved |
| VE-02 | Registry hash rule defines exact covered octets and encoding | **BLOCKED** — BC-02-DEP-002; hash rule is undeclared |
| VE-03 | Registry-issued `raw_input` plus `raw_input_encoding` in octet-exact form | **BLOCKED / NOT BOUND** — the checked-in P-01 byte fixture is not evidence of a Registry-issued, field-bound fixture; do not substitute it for VE-03 |
| VE-04 | Resolvable Boundary Specification v1, Core Interface Spec v1, BC-01, and fixed adapter signature | **BLOCKED** — BC-02-DEP-004 remains open; the accepted artifacts are reported as unresolvable in scope |
| VE-05 | No repository-resident fixture copy on either implementation side; sealed-store transfer | **BLOCKED** — BC-02-OBS-007 records the existing local-copy arrangement and says B-VAL-019 is unfalsifiable while a resident copy remains |

BC-02 §19 further records `input_characterization` vocabulary as unresolved (BC-02-DEP-005). It may affect B-VAL-015, and should be resolved before claiming closure of the complete B-VAL-011…020 package.

The current P-01 adapter programs emit receipts and R-VAL results; their own comments explicitly state that they do **not** execute B-VAL-014 or §4.5. Running them again while VE-01…VE-05 remain unmet would not close the gate and would contradict the specified validation preconditions. No adapter should work around these gaps by inventing registry data, treating a file path as a sealed issuance, or asserting an authority that is not bound.

## 4. Negative control obligations

After prerequisites are discharged and execution is separately authorized, the BC-02 §15.3 controls must be applied to temporary copies; committed fixture material must remain untouched and the sealed-store digest must be re-verified.

At minimum, preserve per-control injected condition, receiver/adapter/source pins, pre/post octet evidence, expected assertion, observed rejection or failure classification, logs, and artifact hashes:
- **BNC-1:** flip one octet in the buffer delivered to one side only; caught by B-VAL-012 and B-VAL-014.
- **BNC-2:** have one adapter construct input from `input_characterization` instead of the received buffer; caught by B-VAL-019 (and B-VAL-012 if not byte-exact).
- **BNC-3…BNC-7:** post-seal write; expected-acceptance leakage; transport interruption; UNKNOWN-to-null conversion; duplicate implementation identity. The contract maps each to its controlling assertion.

**No evidence found in the reviewed pinned artifacts demonstrates that BNC-1 was executed against the current actual receiver flow.** The parser mutation corpus is not a substitute for these BC-02 engineering controls.

## 5. CONF-003 §4.5

The current default-branch artifact [CONF-003](https://github.com/vaidt/aura-specification/blob/11e512365957cd1367062e379bcd655d24048d96/conformance/CONF-003_CANONICAL_SERIALIZATION.md) is version `1.1-DRAFT`, status `DRAFT`. Its §4.5 says an implementation must not accept a prohibited form as digest input; where such an input can be driven to the boundary, the attempt must fail rather than produce a digest. The document itself records §4.5 as `NOT EXECUTED`.

The same §4.5 clause references APS-200 §8.4, while BC-02’s dependency/observability notes report that APS-200 §8.4 is missing on the current default-branch artifact and that reference repair is deferred. Therefore an independent §4.5 execution needs a verified authoritative, bound definition of the prohibited-input set and a runnable invocation path; the current strict receipt-JSON parser tests do not do this.

Evidence required for an independently reviewed §4.5 execution must include, at minimum:
1. The exact governing CONF-003/APS-200 revision and source pins.
2. Exact prohibited-input corpus and provenance for each case.
3. Actual digest-input boundary invocation for each relevant case against the pinned RI-PY and RI-RS implementations, with complete stdout/stderr and exit outcome.
4. Evidence that each prohibited attempt rejected/fails without producing a digest, plus ordinary allowed-input controls.
5. Artifact hashes, test harness/source hashes, environment/runtime pins, independent reviewer’s per-case disposition, and retained raw logs.
6. Explicit separation between receiver handoff/R-VAL evidence, BC-02 B-VAL observations, and §4.5 conformance evidence.

This note does not infer or assign any §4.5 PASS/FAIL. The referenced protocol text is currently DRAFT and its APS-200 §8.4 binding is unresolved in the reviewed source state.

## 6. Gate disposition and next admissible sequence

Current state remains:

```text
P-01 actual handoff evidence (historical)   OBSERVED — ENGINEERING EVIDENCE ONLY
B-VAL-014                                  NOT EXECUTED
BC-02 validation preconditions VE-01…VE-05 BLOCKED
BC-02 BNC-1…BNC-7                           NOT DEMONSTRATED HERE
CONF-003 §4.5                              NOT EXECUTED / NO RESULT
C6 gate                                    BLOCKED_NOT_EXECUTED
authority / governance / release effect     NONE
```

Admissible sequence:
1. Resolve/bind the Registry, hash rule, octet-exact issued fixture, boundary/core interface specs, and remove resident fixture copies; preserve primary evidence for each closure.
2. Obtain the separate custodian authorization required by the contract for BC-02 validation; do not infer authorization from this note or green parser CI.
3. Execute the BC-02 §15 positive procedure and BNC-1…BNC-7 with distinct pinned RI-PY/RI-RS flows; emit the full BC-02 Boundary Validation Report (both records verbatim, B-VAL-011…020 table, control results, unmet-precondition list).
4. Separately resolve the normative CONF-003/APS-200 §8.4 source binding and obtain authorization for actual §4.5 conformance tests. Run those tests against pinned protocol implementations, not just the receipt boundary.
5. Independently audit all raw evidence and the report. Only an authorized decision process may then determine whether a gate state can change.

No source code, normative specification, fixture, governance record, protocol result, or gate state is changed by this note. No PR is promoted or merged.
