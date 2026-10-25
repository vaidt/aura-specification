# AURA C6 Candidate Lab — Source Lock and JSON Pilot

**Status:** DRAFT / EXPLORATORY / NON-NORMATIVE  
**Purpose:** Establish L0 source identity, materialize 47 candidate entries in an isolated run directory, reproduce the pinned baseline at L6, and observe the JSON pilot without assigning expected outcomes.

## 1. L0 source lock

The lab fails closed unless the following baseline identities match exactly:

| Field | Pinned value |
|---|---|
| Repository | `vaidt/aura-specification` |
| Commit | `6b4f3dcc46841bb17fafa3e1b1cc8ea9c0397330` |
| Manifest | `fixtures/corpus/STAGE-C-C6-STRICT-WIRE-MUTATION-CORPUS-v0.1-DRAFT.json` |
| Git blob OID | `d9b4a1f488185a44f7edb233ef8ff180981f0e84` |
| SHA-256 of exact Git blob bytes | `c975cb0a3b02670b63ebb0e2809a2e0cb7c8247c2f0dc1a9829466f4806ea49d` |
| Required baseline size | 27 cases |

The verifier reads the manifest from the exact Git object, not from `main` or a relative path in an unpinned checkout. It also verifies the pinned candidate inventory commit and blob before materialization. The original baseline manifest and its prior results are never written by the candidate materializer.

## 2. Candidate materialization

The active pool is 47 entries from the 50-entry draft inventory. `C6-X-004`, `C6-X-009`, and `C6-X-041` remain excluded from that pool. Each active entry stays `contract_binding_status=UNRESOLVED` and `expected_outcome_policy=CONTRACT_DECISION_REQUIRED`.

Candidate inputs, configs, and seed samples are written under a unique runner-temporary directory. The materialization index is not named `index.json` and does not use the baseline runner's schema; this deliberately prevents accidental substitution into the 27-case path. Exact raw bytes are hashed; invalid UTF-8, BOM, duplicate-key, and non-standard numeric token inputs are not normalized.

Some inventory recipes omit concrete bytes or boundary parameters. This lab pins explicit *exploratory parameterizations* for reproducibility—for example, 65,536 decoded octets for the first size probe, 1,048,576 octets for the second size probe, and depth 256 for the nesting probe. These are test inputs, not claims about a normative configured limit or expected parser outcome.

`C6-X-050` is represented as a bounded generator configuration with eight individually identified fixed samples (`C6-X-050-S001` through `C6-X-050-S008`). The generator is deterministic, uses no random source, caps the seed count at eight, and caps each sample at 2,000,000 bytes. The fuzz set is not one parser case and is not inserted into the baseline manifest.

## 3. JSON pilot

The first candidate observation pass is limited to `C6-X-013`–`C6-X-020`. RI-PY and RI-RS are pinned to:

- RI-PY / Core: `fe3be05794d3f254d98af1464e598e5b9be2e369`
- RI-RS / Aura-Guard: `feab2d9c369cd5f8cbabe10d713d278b0b09da8b`

The observers record actual result/code, exact input digest and byte count. They do not assign expected result/code. The differential report classifies implementation agreement or disagreement, while keeping contract binding unresolved. A mismatch or incomplete execution fails closed and still preserves whatever artifacts were produced.

## 4. L6 baseline regression

Both `x86_64` and `aarch64` rerun the baseline using the pinned source commits above, baseline commit `6b4f3dcc46841bb17fafa3e1b1cc8ea9c0397330`, and integrated harness commit `38821305ddb93eca96d9eb86e53d5c2db5d91295`.

The generated materialized index, RI-PY report, and RI-RS report must match the recorded historical SHA-256 values byte-for-byte:

- Index: `445d5808cb76a24b916a91e91636d4ce10ac3b0239f9eb2f474264783bc41181`
- RI-PY: `cfdbd0fbbc1442bba0b7a70a5bf7c76fc5ecd9cb2dabe27ffe4379053196a6a4`
- RI-RS: `b289367fc2e19f0666d202d35eb257d795ff18c589d7d0323c202e6a4636e25b`

Historical run: [#40176350679](https://github.com/vaidt/aura-specification/actions/runs/40176350679). The historical archive digests are recorded as provenance references; L6 does not attempt to reproduce GitHub's ZIP container format.

## 5. Evidence package and governance boundary

The final package exposes nine logical evidence documents: Source Lock, inventory snapshot, materialization index, RI-PY report, RI-RS report, differential report, baseline regression report, integrity manifest, and disposition report. A supporting-evidence directory retains raw baseline bytes, physical candidate inputs, parameterized configs, fuzz seeds, and per-architecture baseline outputs. The integrity manifest covers all package files except itself to avoid a circular self-hash.

All reports must preserve `authority=NONE`, `governance_effect=NONE`, `authorization_effect=NONE`, and `release_effect=NONE`. The operational result may be `CONTRACT_UNRESOLVED`; that is expected while expected outcomes remain unratified. A successful technical run cannot close C6, CONF-003, DQ-006, M1/G1, or authorize release.

**Frozen statuses:** `C6_GATE_STATUS=BLOCKED_PENDING_EVIDENCE_REVIEW`; CONF-003 `PARTIAL`; DQ-006 `OPEN`; M1/G1 `BLOCKED / NOT PROVEN`; release `NO-GO`. Existing PR states are not modified by this lab branch.
