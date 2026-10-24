# BC-02.1 Strict Receipt JSON Consumer — Interface Draft

**Status:** DRAFT · NON-NORMATIVE · NOT RATIFIED  
**Stage:** C6 preparation  
**Authority / governance / authorization / release effect:** NONE

## 1. Boundary and public entry points

The consumer receives the original receipt-envelope bytes. It must not receive a previously parsed object/map because ordinary JSON object parsing can erase duplicate member occurrences.

- RI-PY: `parse_receipt_json(raw_json: bytes) -> BoundaryReceipt`, raising `ReceiptParseError(code, detail)` on rejection.
- RI-RS: `parse_receipt_json(raw_json: &[u8]) -> Result<BoundaryReceipt, ReceiptParseError>`, where `ReceiptParseError.code` is the stable category and `detail` is diagnostic only.

Both functions consume **receipt JSON transport**, not the original artifact. The raw artifact remains an opaque octet sequence. An artifact containing NUL or non-UTF-8 octets is valid input; the separate JSON envelope itself must be UTF-8.

## 2. Required behavior

1. Validate UTF-8 before JSON interpretation; reject malformed envelope bytes.
2. Parse JSON while preserving duplicate-member detection at every nesting level. Reject duplicate keys before interpreting the receipt.
3. Require an object and exactly the BC-02.1 top-level and nested fields. Reject unknown keys, including `conformance_result`, `verdict`, or other extra fields; reject missing keys.
4. Reject `null` for every required field. Do not infer defaults.
5. Require `schema_id = BC-02.1-COMMON-RECEIPT` and integer `schema_version = 1`. A JSON boolean is not an integer.
6. Require `handoff.status` in the closed domain `TRANSFERRED | NOT_TRANSFERRED | ERROR`.
7. Require a Base64 **string** for `received.raw_octets`. Strictly decode it, require canonical padded Base64, and permit the empty string only for the empty octet sequence.
8. Require a non-negative integer `received.octet_length) equal to the decoded octet count.
9. Require `received.recomputed_sha256` to be 64 lowercase hexadecimal characters equal to SHA-256 of the decoded raw octets. Never hash the Base64 characters.
10. Require all provenance and identity strings to be non-empty.
11. Return the typed receipt only after all checks succeed. The returned type has no conformance-result field.

The parser may accept JSON member order/insignificant input whitespace. Deterministic serialization rules in BC-02.1 §12 apply to emitters; they do not authorize lenient field interpretation by the consumer.

## 3. Stable rejection categories

The following code strings are an engineering interface for this Draft, not normative protocol statuses:

| Code | Meaning |
|---|---|
| `INVALID_UTF8` | Receipt-envelope bytes are not UTF-8. |
| `INVALID_JSON` | Malformed JSON or non-standard JSON numeric token. |
| `DUPLICATE_KEY` | Any duplicate object member at any nesting level. |
| `INVALID_SHAPE` | Expected object is not an object. |
| `MISSING_FIELD` | Required schema field is absent. |
| `UNKNOWN_FIELD` | Field outside the exact BC-02.1 schema. |
| `NULL_NOT_ALLOWED` | Required field has a JSON null value. |
| `TYPE_MISMATCH` | A field has the wrong JSON primitive type. |
| `INVALID_VALUE` | Typed value violates the field's value domain or non-empty rule. |
| `SCHEMA_ID_MISMATCH` | Unsupported schema identity. |
| `SCHEMA_VERSION_MISMATCH` | Unsupported integer schema version. |
| `INVALID_BASE64` | Base64 is malformed, unpadded, or non-canonical. |
| `LENGTH_MISMATCH` | Declared octet length differs from decoded bytes. |
| `DIGEST_MISMATCH` | Supplied receiver-derived digest differs from SHA-256 of decoded bytes. |

A rejection category is transport diagnostics only. It is not PASS/FAIL, a conformance result, a ratification decision, an authorization, or a release state.

## 4. Byte-identical mutation corpus

`fixtures/corpus/STAGE-C-C6-STRICT-WIRE-MUTATION-CORPUS-v0.1-DRAFT.json` defines the seed receipt and mutation operations. `scripts/stage_c/materialize_c6_wire_corpus.py` generates each test input once and writes its exact bytes to a separate file plus an index containing byte length and SHA-256.

Both RI-PY and RI-RS must read those **same generated files**, independently verify the input length and SHA-256 in the index, and produce the declared accept/reject outcome and rejection category. The mutation is not independently re-serialized by each implementation under test. This makes byte identity inspectable rather than assumed.

The corpus covers the positive raw-octet/empty-octet controls, duplicate keys, invalid UTF-8 and JSON, exact field sets, authority-bearing/unknown fields, null/type/value errors, status and schema version, Base64, length, and digest integrity.

## 5. Gate discipline

Implementation and local unit tests do not by themselves close C6. The dedicated CI run must materialize the corpus once, execute both native consumers against those exact files, preserve source pins, per-case input SHA-256, outcomes and test logs, and report parity only if every case matches. Any missing implementation, skipped corpus test, source-pin mismatch, error-category disagreement, or hash mismatch blocks C6.

This document and the tests introduce no normative change. C6 remains **BLOCKED** until the shared corpus run is complete and the resulting evidence is reviewed.
