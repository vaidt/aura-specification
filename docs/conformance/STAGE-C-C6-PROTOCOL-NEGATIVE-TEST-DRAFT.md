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

The inspected implementations do not yet expose equivalent receipt-JSON consumer entry points:

- **RI-PY** has a typed receipt constructor, deterministic serializer, Base64 decoder helper, and R-VAL-001..012 model validator. A full inverse parser for an arbitrary BC-02.1 JSON receipt was not found.
- **RI-RS** builds typed receipt values and validates them, while the handoff binary emits a separate Base64 transport mapping. The native Rust DTO has `raw_octets: Vec<u8>`, whose generic serde JSON form is a number array, not the contract's Base64 string. No reciprocal BC-02.1 wire receipt parser was found.
- The Rust structs use derived Serde deserialization without `deny_unknown_fields`; the derived boundary type can therefore ignore unrecognized keys. That behavior is not sufficient evidence of strict BC-02.1 consumer conformance.
- Existing unit tests mainly exercise construction and typed-object validation. They do not amount to one shared negative receipt-envelope corpus executed through equivalent Python and Rust wire consumers.

These are C6 blockers to preserve, not reasons to relabel test-plan checks as passing.

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

A green **preparation** workflow only means that the case inventory and the tests that can be run on the currently available surfaces are reproducible. It is not a C6 PASS.

## 6. Acceptance criteria for eventual C6

C6 cannot be marked PASS until all the following are true:

1. A byte-accurate valid BC-02.1 wire receipt is accepted by both independent implementations.
2. The same byte-for-byte mutation corpus is run through both native wire-consumer paths.
3. Every invalid receipt is rejected at the defined contract boundary, including unknown/authority fields, wrong Base64 representation, missing/null fields, malformed UTF-8/JSON, and duplicate keys.
4. The negative outcomes are recorded in an implementation-independent matrix with source SHA, input SHA, adapter version, process exit/error category, and raw output artifact hashes.
5. No case is passed solely by a test-side oracle or by constructing a typed object without exercising the external contract.
6. C6 test results do not change DQ/CONF governance states, authority continuity, implementation authorization, or release readiness.

Until the missing wire-consumer boundary is implemented and the same tests execute against both implementations, the C6 gate remains **BLOCKED**. C5 does not authorize C6 completion, ratification, or release.
