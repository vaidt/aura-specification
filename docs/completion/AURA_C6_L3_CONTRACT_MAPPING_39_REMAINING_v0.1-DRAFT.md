# AURA C6 L3 — Contract Mapping for 39 Remaining Candidates

**Status:** DRAFT / CONTRACT REVIEW REQUIRED / NON-NORMATIVE  
**Scope:** The 39 active C6 candidates not included in the completed JSON observation pilot.  
**Effect:** None. This document does not authorize parser execution, lock expected codes, ratify BC-02.1, or change C6/CONF-003/DQ-006/M1/G1/release status.

## 1. Controlling source evidence

| Source | Pinned identity | Source status |
|---|---|---|
| Candidate inventory | `vaidt/aura-specification@3a8e7ac3e26faa92fe383d090fe366b72ff438ff`, blob `06a4e8827fb589e3a549944c71718291d1345f16` | `DRAFT_NON_NORMATIVE` |
| BC-02.1 schema | `6b4f3dcc46841bb17fafa3e1b1cc8ea9c0397330`, blob `f40f7a2ea246f382d12490a6489159f9e226fd17` | `CONSTRUCTED`, conformance blocked, normative authority NONE |
| Error taxonomy record | same commit, blob `7573f83762b8d02f98f0665542a67722fcf0b616` | Ratification pending execution; implementation authorization not granted |
| APS-200 | same commit, blob `198eee23f12e1db7b3417d3b359c4f912142e984` | Draft |
| C6 contract-negative manifest | same commit, blob `a440742ebcd7f6b3b6cb396e30dfc8f95362d4f0` | Draft non-normative; normative effect NONE |

BC-02.1 §12 states exact schema fields only, no additional fields, explicit values, UTF-8, lexicographic member order, no insignificant whitespace, canonical integer spelling, Base64 for raw-octet transport, and no null. §6 requires unambiguous decoding, length equal to decoded octet count, and digest over raw decoded octets rather than Base64 text. §4 requires fixture identity fields to be present. §§7–8 preserve receiver, implementation, adapter, and source-commit identities, but do not specify every identity syntax or every empty-string/equality rule.

The error taxonomy record contains a material governance conflict: its header says `Ratification_Status: PENDING_EXECUTION` and its implementation authorization says `NOT_GRANTED`, while a later subsection claims `Normative_Effect: EFFECTIVE` for P-012. The mapping cannot resolve that conflict by inference.

## 2. Mapping disposition

The machine-readable companion `AURA_C6_L3_CONTRACT_MAPPING_39_REMAINING_v0.1-DRAFT.json` contains all 39 active IDs, exact source references, rule mappings or identified gaps, and explicit outcome fields. Every candidate remains:

- `contract_binding_status = UNRESOLVED`
- `expected_outcome_policy = CONTRACT_DECISION_REQUIRED`
- `expected_code = null`
- `expected_result = null`
- `execution_authorization = NOT_GRANTED`

The field `mapping_disposition` names the rule family or missing contract decision; it is not an approved error code. `proposed_diagnostic_family` is `NONE_LOCKED` for every candidate.

## 3. Decision table

| Candidate(s) | Contract mapping / gap | Why exact expected code remains unset |
|---|---|---|
| C6-X-001–003, -005, -006 | Missing required objects; BC-02.1 §§3, 12 | Schema requires all declared fields, but parser diagnostic taxonomy for this boundary is not authorized. |
| C6-X-007, -008, -010–012 | Unknown nested fields; BC-02.1 §12 | The no-additional-fields rule supports rejection as a rule-level expectation only if this schema is adopted; exact code remains unresolved. |
| C6-X-021–026 | Base64 alphabet, whitespace, padding, pad bits, non-ASCII, line breaks; BC-02.1 §6, §12 | Decoding must be unambiguous; specific variant handling and error precedence are not fully defined. |
| C6-X-027–028 | Positive Base64/raw-octet controls; BC-02.1 §6 | Positive controls must not be assigned a rejection code; expected positive outcome still needs controlled contract ratification. |
| C6-X-029 | Null length; BC-02.1 §§10, 12 | Null is prohibited, but exact parse code is not defined. |
| C6-X-030 | String length instead of integer; BC-02.1 §12 | JSON integer required; exact parse code not defined. |
| C6-X-031–032 | Exponent/negative-zero integer spellings; BC-02.1 §12 | Alternate numeric forms are prohibited, but the exact lexical-vs-semantic parsing error is unspecified. |
| C6-X-033, -048 | Size boundary probes | No maximum receipt/envelope/raw-octet length is defined. The chosen values are exploratory, not contract limits. |
| C6-X-034–035 | Integer overflow/negative boundary; BC-02.1 §§6, 12 | Length must equal decoded byte count, but overflow handling and signed/range policy are unspecified. |
| C6-X-036–038 | Uppercase/non-hex/wrong-length digest text | Digest semantics are SHA-256, but exact allowed wire representation/case/length is not fully specified by BC-02.1. |
| C6-X-039–040 | Digest over Base64 text or stale digest after byte change; BC-02.1 §6, R-INV-03 | Source clearly requires digest over decoded raw octets. The proposed diagnostic family could be digest mismatch, but exact taxonomy authorization remains unresolved. |
| C6-X-042–043 | Empty fixture/environment identity | Required presence is specified; non-empty string semantics are not explicitly specified. |
| C6-X-044 | Receiver/adapter ID equality | The schema forbids using implementation ID as an implicit alias; it does not explicitly prohibit receiver ID equalling adapter ID. Clarification required before rejection. |
| C6-X-045 | Malformed source commit | Source-commit identity must be preserved; syntax, length and full-SHA requirements are not specified by BC-02.1. |
| C6-X-046 | `CONFORMANT` in metadata | Conformance-result authority is excluded; the explicit closed domain is scoped to `handoff.status`. Applying it to all string fields requires clarification. |
| C6-X-047 | Missing receiver + null version | Both are defects; no contract-defined error precedence. |
| C6-X-049 | Nesting depth probe | No maximum JSON depth is defined. |
| C6-X-050 | Eight deterministic seeds | Must be triaged as S001–S008 individually; a single result code for an aggregate is invalid. |

## 4. Per-seed treatment for C6-X-050

| Sub-ID | Probe | Contract reference / gap |
|---|---|---|
| S001 | Trailing byte after JSON | Strict single-document/no-trailing-data requirement needs an explicit controlling parse-boundary clause. |
| S002 | UTF-8 BOM prefix | BC-02.1 requires UTF-8, but BOM handling is not explicitly specified. |
| S003 | Truncated JSON | Malformed JSON rejection is consistent with strict transport, but exact contract/code is not locked here. |
| S004 | Invalid UTF-8 in JSON receipt envelope | UTF-8 receipt transport requirement; keep separate from arbitrary raw artifact octets. |
| S005 | Duplicate top-level key | Duplicate-key rejection is described in draft C6 negatives; controlling ratified requirement/code still needs approval. |
| S006 | Escaped-equivalent duplicate key | Duplicate semantics after JSON escape decoding need an explicit exact contract clause. |
| S007 | Stale digest after byte change | BC-02.1 §6 / R-INV-03 raw-octet digest invariant; exact diagnostic map unresolved. |
| S008 | Nesting depth 256 | No normative depth limit; treat only as a bounded resource observation. |

## 5. Required decisions before exact-code lock

1. Ratify/authorize the BC-02.1 wire-consumer contract and reconcile the taxonomy record’s ratification/authorization fields.
2. Approve a version-bound error map for this parser boundary; do not assume Wave 1 diagnostic codes apply automatically to these strict-wire parse failures.
3. Specify digest text representation, non-empty identity requirements, source-commit syntax, Base64 canonicality rules, BOM/duplicate-key semantics, error precedence, and any size/depth resource limits.
4. Give C6-X-044 an explicit identity uniqueness/equality rule or disposition it as an observational control rather than a negative test.
5. Bind each expectation to an immutable ratified contract revision and independent review before converting `expected_code` from null.

## 6. Governance boundary

`authority=NONE`, `normative_effect=NONE`, `governance_effect=NONE`, `authorization_effect=NONE`, `release_effect=NONE`.

The inventory’s three exclusion tombstones stay excluded. The 27-case baseline is not modified. Existing PR statuses stay unchanged. No code is assigned by inference from the 8/8 observed JSON pilot.
