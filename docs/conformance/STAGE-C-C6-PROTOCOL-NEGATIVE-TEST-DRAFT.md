# Stage C — C6 Protocol Contract Negative Tests (Draft)

**State:** DRAFT · NON-NORMATIVE · NOT RATIFIED  
**Branch:** `experiment/stage-c-c6-contract-negative-20261024`  
**Depends on:** C5 technical evidence, without inheriting authority from it  
**Gate state:** `PREPARATION_ONLY / C6 BLOCKED`  
**Authority, governance, authorization, and release effect:** NONE

## 1. Purpose

C6 must test protocol-boundary rejection semantics, not merely object construction or a test-plan inventory. This Draft prepares a shared mutation corpus and CI wiring around the BC-02.1 common receipt contract. It is explicitly not a completed C6 execution.

## 2. Source inspection findings

The inspected contract defines a strict wire schema: all required fields are explicit, null is prohibited, extra fields are prohibited, raw octets are Base64 in JSON transport, and the receiver-derived digest must equal SHA-256 of the decoded raw octets.

The experimental branches now contain separate receipt-envelope entry points:

- **RI-PY** adds `parse_receipt_json(raw_json: bytes)` and `ReceiptParseError(code, detail)` in Draft PR [#8](https://github.com/vaidt/aura-poc-a-core-v3.3/pull/8).
- **RI-RS** adds `parse_receipt_json(raw_json: &[u8])` and a typed `ReceiptParseError` to the spec-side receiver on this C6 Draft branch.
- Both entry points accept original envelope bytes, detect duplicate keys before interpretation, enforce exact field sets and Base64 transport, and verify decoded length and SHA-256.
- Direct derived DTO deserialization remains a lower-level surface and must not be confused with the strict wire API. Consumers and tests must call `parse_receipt_json`, not `serde_json::from_value::<BoundaryReceipt>`.
- A shared mutation manifest, one-time materializer, and language-specific runners have been added. The shared corpus has **not yet been verified by a completed CI run**, so these implementations are experimental and the parity claim remains NOT ESTABLISHED.

The current C6 gate remains blocked until the exact same materialized receipt JSON byte files are run against both immutable implementation pins and every declared error category agrees.

## 3. Negative-test categories

The manifest covers the following independent assertions:

1. Invalid handoff status values and prohibited result synonyms.
2. Missing/empty fixture identity and handoff method.
3. Hex/Base64 text supplied at the raw-octet API instead of bytes.
4. Mismatched byte length or receiver-derived SHA-256.
5. Wrong schema identity/version.
6. Missing receiver, implementation, adapter, or environment provenance.
7. Unknown or authority-bearing receipt keys.
8. Base64 wire decoding, malformed Base64, and decoded-octet integrity.
9. Missing/null fields, incorrect nested types, invalid integer forms, and malformed receipt JSON.
10. Duplicate JSON keys.
11. Malformed UTF-8 at the receipt-envelope boundary.
12. Positive boundary controls proving arbitrary raw artifact bytes are not mistakenly parsed as a UTF-8 receipt envelope.

The complete case inventory is in `fixtures/corpus/STAGE-C-C6-CONTRACT-NEGATIVES-v0.1-DRAFT.json`. Each row names the required result and the exact current implementation limitation, where one is known.

## 4. Boundary separation

Two objects must not be conflated:

- **Artifact octets:** receiver intake is intentionally binary. Embedded NUL, non-UTF-8 bytes, and empty byte sequences are valid observations. They are not automatically malformed.
- **Receipt JSON:** this is a separate structured transport. UTF-8 validity, JSON shape, strict field sets, Base64 decode, decoded length, and digest consistency are checked here.

C6 must never reject arbitrary artifact bytes solely because they are not valid UTF-8. It must reject malformed receipt-envelope bytes before interpreting them as a receipt.

## 5. Test infrastructure prepared here

The Draft adds:
- a machine-readable negative-case manifest;
- an inventory validator that refuses duplicate IDs, missing fields, untracked gap dispositions, or accidental governance-effect labels;
- a Python native-boundary test set against the exact pinned RI-PY commit;
- a Rust integration test set against the specification-side RI-RS receiver;
- a read-only CI workflow that uploads its inventory/report and preserves the source pins.

The native tests distinguish:
- rejection behavior already available on the typed receiver APIs;
- reproducible known wire-consumer gaps;
- cases that cannot honestly be executed until the wire-consumer interface is defined.

A green **preparation** workflow only means the candidate strict consumers and byte-identical corpus test harness completed against the recorded experimental pins. It is not a C6 PASS until the resulting per-case hashes, outcomes, error categories, and source pins are independently reviewed.

## 6. Acceptance criteria for eventual C6

C6 cannot be marked PASS until all the following are true:

1. A byte-accurate valid BC-02.1 wire receipt is accepted by both independent implementations.
2. The same byte-for-byte mutation corpus is run through both native wire-consumer paths.
3. Every invalid receipt is rejected at the defined contract boundary, including unknown/authority fields, wrong Base64 representation, missing/null fields, malformed UTF-8/JSON, and duplicate keys.
4. The negative outcomes are recorded in an implementation-independent matrix with source SHA, input SHA, adapter version, process exit/error category, and raw output artifact hashes.
5. No case is passed solely by a test-side oracle or by constructing a typed object without exercising the external contract.
6. C6 test results do not change DQ/CONF governance states, authority continuity, implementation authorization, or release readiness.

Until the missing wire-consumer boundary is implemented and the same tests execute against both implementations, the C6 gate remains **BLOCKED**. C5 does not authorize C6 completion, ratification, or release.
