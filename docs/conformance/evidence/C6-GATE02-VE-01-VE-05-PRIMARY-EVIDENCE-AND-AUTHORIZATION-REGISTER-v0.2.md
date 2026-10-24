# AURA GATE-02 / C6 — Primary Evidence and Authorization Closure Register v0.2

**Status:** BLOCKED — NOT AUTHORIZED — NO GATE PROMOTION  
**Review date:** 2026-10-24  
**Target:** BC-02 §§15/19, VE-01…VE-05; B-VAL-014 and BNC-1…BNC-7; separate CONF-003 §4.5 execution  
**Review branch:** `experiment/stage-c-c6-strict-wire-consumer-20261024`  
**Reviewed branch head before this record:** `0f5da6c54c32fb2f20066be851d7238c4a749334`  
**Authority / governance / authorization / release effect of this record:** NONE.

This is an evidence inventory and blocker register only. It does not close a precondition by declaration, approve a governance act, run BC-02 validation, run BNC controls, or create a conformance result.

## 1. Executive decision

**No newly found primary/constitutive evidence closes VE-01…VE-05, and no effective Custodian execution authorization was found.** The gate therefore cannot advance.

The following statements must be kept separate:
- Historical P-01 receipts demonstrate a prior engineering handoff of the same 15 octets through RI-PY and RI-RS.
- The custodian reconciliation record states that the formal definition of B-VAL-014 is BC-02 §14’s “Raw input preserved” assertion, but **B-VAL-014 remains NOT EXECUTED**.
- The GATE-02 authorization artefact on `main` remains `PROPOSED GOVERNANCE ACT — NOT APPROVED — NOT EFFECTIVE`; its ratification identity, effective date, repository/ref scope, and evidence/conformance authority fields remain `TBD`.
- The historical merge of PR #3 merged the *draft text*, not a ratification act. Its PR body explicitly preserved `NOT APPROVED`, `NOT EFFECTIVE`, `B-VAL-014 NOT AUTHORIZED`, and `BNC-1 NOT AUTHORIZED`.

## 2. Source pins reviewed

| Source | Pinned ref / object | Audit significance |
|---|---|---|
| [BC-02 construction contract §15/§19](https://github.com/vaidt/aura-specification/blob/e2066bd/conformance/boundary/BC-02_IMMUTABLE_FIXTURE_HANDOFF.md) | source branch commit `e2066bdd05664cc63656ce5623319bccf817acb4`; blob `9cfbc0fe66578dbb52cb6012f3ea03adcb48c40c` | Normative engineering preconditions; validation is not authorized by this document and cannot begin while §19 blockers remain |
| [Custodian closure record](https://github.com/vaidt/aura-specification/blob/main/conformance/boundary/BC-02-CUSTODIAN-CLOSURE-RECORD.md) | main blob `044f16a83ef42b9c9356372bf3def805b2a43404` | Explicitly says it creates no authority and does not authorize B-VAL-014 |
| [B-VAL-014 definition reconciliation](https://github.com/vaidt/aura-specification/blob/main/conformance/boundary/B-VAL-014-DEFINITION-RECONCILIATION-RECORD.md) | main blob `281b29ca77dded2bbeb16ecc2fe916774ac57bb6` | Definition resolved; execution not authorized by this record; PRE-01, PRE-02, PRE-03 identified |
| [GATE-02 execution authorization draft](https://github.com/vaidt/aura-specification/blob/main/governance/AURA_GATE_02_EXECUTION_AUTHORIZATION_v1.0-DRAFT.md) | main blob `edd0d202515cfa63f516aad61639ba83d884d2af` | `NOT APPROVED — NOT EFFECTIVE`; requested authority only; ratification fields TBD |
| [Chief Architect → Custodian scope bridge](https://github.com/vaidt/aura-specification/blob/0f5da6c54c32fb2f20066be851d7238c4a749334/conformance/boundary/BC-02-Q1-CHIEF-ARCHITECT-CUSTODIAN-SCOPE-BRIDGE.md) | blob `c2df3807a96b02befa7896fe27524d664ddf6641` | Draft/non-binding; no binding approval or delegation recorded |
| [Existing real-flow gap report](https://github.com/vaidt/aura-specification/blob/0f5da6c54c32fb2f20066be851d7238c4a749334/docs/conformance/evidence/C6-REAL-FLOW-GAP-AND-EXECUTION-PLAN-v0.1.md) | commit `0f5da6c54c32fb2f20066be851d7238c4a749334`; blob `f5ed98bef1022904bedbb221908c9092f3761582` | Prior assessment, preserved as history |

Repository-tree search at reviewed head did not locate a resolvable `CONFORMANCE_FIXTURE_REGISTRY_v1` contract, a bound Registry entry for P-01, or the required Boundary Specification v1 / Core Interface Spec v1 / BC-01 set. Code search for the Registry symbol surfaced only unrelated documentation-normalization records; it did not identify a resolvable governing Registry document.

## 3. VE-01…VE-05 closure register

The controlling BC-02 contract §15 explicitly says validation MUST NOT begin with any unmet precondition. The contract §19 says BC-02 validation is not authorized by that document and cannot be entered while any blocking dependency remains open.

| VE | Primary evidence required to close | Finding at reviewed refs | Disposition |
|---|---|---|---|
| **VE-01** | Versioned, field-bound `CONFORMANCE_FIXTURE_REGISTRY_v1` and a resolvable Registry entry for the chosen fixture | No governing Registry contract or bound entry located in the reviewed current tree | **OPEN — NOT CLOSED** |
| **VE-02** | Registry-owned declaration of the exact `fixture_hash` rule: covered octets, encoding, and verification procedure | BC-02-DEP-002 remains open; the rule is expressly recorded as undeclared | **OPEN — NOT CLOSED** |
| **VE-03** | Registry-issued `raw_input` plus `raw_input_encoding` in an octet-exact representation, bound to issuance identity | Historical checked-in 15-byte P-01 file and receipts are not, by themselves, proof of a currently bound Registry-issued artifact meeting the VE-03 contract | **OPEN — NOT CLOSED** |
| **VE-04** | Resolvable Boundary Specification v1, Core Interface Spec v1, BC-01, plus confirmed receiver/adapter interface signatures | BC-02-DEP-004 remains open; specifications are recorded as unresolvable in the in-scope repositories | **OPEN — NOT CLOSED** |
| **VE-05** | Evidence that neither implementation side has a resident fixture copy; sealed-store provenance and transfer from that store to each receiver | BC-02-OBS-007 records the local-copy arrangement; B-VAL-019 is considered unfalsifiable while a resident reconstruction source remains | **OPEN — NOT CLOSED** |

Adjacent dependency **BC-02-DEP-005** (`input_characterization` vocabulary) remains unresolved and affects B-VAL-015/full B-VAL-011…020 report completeness. Do not convert any UNKNOWN into ABSENT, PASS, or a closed dependency by implication.

### Evidence package required for a legitimate closure record

Each VE closure needs new primary evidence, not an assertion copied into this summary:
- **VE-01:** authoritative Registry contract file/revision, issuing authority, Registry entry ID/version, exact source ref/blob, and field mapping.
- **VE-02:** same-authority Registry text declaring which octets are hashed and the encoding, plus an independently reproducible digest calculation linked to that Registry rule.
- **VE-03:** issuance record binding fixture ID, artifact identity, exact byte length, raw-input encoding, issuance ID, and byte digest; raw artifact retained byte-for-byte and independently hashed.
- **VE-04:** exact refs/blobs for Boundary Specification v1, Core Interface Spec v1, and BC-01; a reviewed mapping from each specification to the actual adapter function signatures and data fields.
- **VE-05:** inspected, hash-pinned evidence of no resident fixture copies on both receiver sides; sealed-store policy/identity; record of the buffer handed from the sealed store to each receiver; pre-transfer/post-receipt hash/length comparisons.

A single secondary note, CI summary, parser test, or receiver-produced receipt is not enough to close an upstream authority, Registry, interface, or sealed-storage prerequisite.

## 4. B-VAL-014: definition versus authorization

The [reconciliation record §12/§16](https://github.com/vaidt/aura-specification/blob/main/conformance/boundary/B-VAL-014-DEFINITION-RECONCILIATION-RECORD.md) establishes the controlling BC-02 §14 definition and explicitly preserves three unmet preconditions:
- **PRE-01 (material):** the BC-02 contract uses `BoundaryHandoffRecord` terms `receipt_digest`, `receipt_digest_source`, `input_segment_sha256`, and `raw_input_encoding`; the historical receipts use BC-02.1 `BoundaryReceipt` terms such as `received.recomputed_sha256` and `received.raw_octets`. No Custodian-declared field mapping or supersession declaration binds those vocabularies. Do not infer that mapping from implementation behavior.
- **PRE-02:** BNC-1 has never been executed against the named assertions.
- **PRE-03:** Registry/hash binding is still open and constrains B-VAL-011/012 even though the narrow formal B-VAL-014 definition does not itself reference the Registry.

The authorization draft is explicitly human-only. It says the agent can prepare/route but cannot issue the delegation; its ratification record leaves authority basis, decision ID, ratification/effective dates, authorized ref, evidence location, conformance authority and evidence authority as TBD. A source search found no effective ratification artefact.

The historical [PR #3](https://github.com/vaidt/aura-specification/pull/3) was merged on 2026-09-25 as a documentation-only draft. Its PR body says `PROPOSED`, `NOT APPROVED`, `NOT EFFECTIVE`, `B-VAL-014 NOT AUTHORIZED`, and `BNC-1 NOT AUTHORIZED`. Merge status does not alter those explicit states.

**Disposition:** B-VAL-014 remains **NOT EXECUTED / NOT AUTHORIZED**. No BNC control was run under this review.

## 5. Required authorization record

Before execution begins, a competent human/governance act must be ratified and recorded as effective. It must at minimum bind:
1. ratifying authority and authority basis;
2. decision/ratification ID and effective date;
3. exact repository, ref/commit, paths, and implementation identities;
4. technical scope: BC-02 §15 positive procedure, B-VAL-011…020 as applicable, BNC-1…BNC-7, evidence collection and retention;
5. conformance boundary, evidence authority and separation from any §4.5 result;
6. explicit acknowledgement of PRE-01/02/03 and exact closure/disposition of each relevant precondition;
7. exit criteria, fail-closed behavior, reviewer independence and no-effect limits.

An effective authorization for B-VAL-014/BNC-1 does not automatically authorize all BC-02 validation or CONF-003 §4.5. Scope must be explicit. The current draft only proposes GATE-02/B-VAL-014 and BNC-1; it cannot be treated as authorization for BNC-2…BNC-7 or §4.5.

## 6. Separate CONF-003 §4.5 gate

Do not fold §4.5 into receiver handoff or B-VAL evidence. At reviewed default-branch source, CONF-003 is `1.1-DRAFT`, status `DRAFT`, and §4.5 points to APS-200 §8.4. The BC-02 and governance audit notes report that APS-200 §8.4 is not present in the current default-branch text, and reference repair was deferred. Therefore a valid §4.5 run still needs:
- bound, authoritative revisions of CONF-003 and APS-200 containing the prohibited-input domain;
- exact case corpus and an ordinary allowed-input control corpus, all source-pinned;
- an actual digest-input boundary invocation on pinned RI-PY and RI-RS, with full stdout/stderr, exit status, and proof a prohibited input rejected rather than produced a digest;
- explicit separation of engineering handoff, B-VAL observations, and conformance evidence;
- its own authorization, if required by the controlling governance framework, plus independent review.

Until the controlling source binding and authorization are resolved, §4.5 remains **NOT EXECUTED / NO RESULT**. Do not run invented cases against a guessed interpretation of `APS-200 §8.4`.

## 7. Gate decision / next admissible actions

```text
VE-01  OPEN
VE-02  OPEN
VE-03  OPEN
VE-04  OPEN
VE-05  OPEN
GATE-02 authorization  NOT APPROVED / NOT EFFECTIVE
B-VAL-014              NOT EXECUTED / NOT AUTHORIZED
BNC-1…BNC-7            NOT DEMONSTRATED BY THIS REVIEW
CONF-003 §4.5          NOT EXECUTED / NO RESULT
C6                      BLOCKED_NOT_EXECUTED
authority/governance/release effect  NONE
```

Admissible order:
1. Produce and verify the primary source documents and records listed for VE-01…VE-05; bind each item to exact source refs/blobs and, where relevant, independent cryptographic checks.
2. Resolve PRE-01 through a competent Custodian field-binding or explicit supersession decision. Preserve the historical receipts unchanged.
3. Obtain an effective human-ratified authorization with the exact repository/ref/scope/evidence boundaries; do not infer it from a merged draft.
4. Only then execute BC-02 §15 with the actual sealed artifact flow and BNC-1…BNC-7, retaining both receipts/records verbatim, per-assertion outcomes, control logs, before/after bytes and hashes, and cross-host deterministic serialization evidence.
5. Separately bind the authoritative CONF-003/APS-200 §8.4 texts and authorized negative/positive corpus; execute §4.5 against actual digest-input boundaries and retain per-case results.
6. Independently review all evidence and issue a disposition. Until then the gate stays blocked.

No protocol/source semantics, fixture, authorization, governance status, or release state is modified by this register. No gated tests are run by this register.
