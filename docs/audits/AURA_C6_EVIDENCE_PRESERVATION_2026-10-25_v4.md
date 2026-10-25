# AURA C6 Evidence Preservation v4 — 2026-10-25

**Record class:** technical evidence preservation; non-constitutive  
**Package SHA-256:** `1f6fff934f98f2ed84f0a75d3885b399807c0bfaa8a328f2c91adf59dbb93f52`  
**Package size:** 1,189,564 bytes; 37 files; 17 embedded ZIP archives  
**Archive integrity:** ZIP test PASS; all 36 entries in `SHA256SUMS.txt` verified; embedded runner handoff checksums verified.  
**Preservation disposition:** v3 is retained byte-for-byte inside v4 and remains separately available by its earlier digest.

## Current technical baseline

- Repository: `vaidt/aura-specification`
- Candidate branch: `experiment/c6-candidate-lab-l0-l6-20261025`
- Candidate commit: `6d7511c52dae79a58b80dfbabe594141abbb980d`
- Candidate workflow: [40203268967](https://github.com/vaidt/aura-specification/actions/runs/40203268967)
- Draft Conformance workflow: [40203273177](https://github.com/vaidt/aura-specification/actions/runs/40203273177)

All five Candidate Lab jobs completed SUCCESS: hosted L0/L2 source-lock and materialization, L6 on x86_64, L6 on aarch64, L4–L5 JSON observation pilot, and L7 non-constitutive evidence assembly. The Draft Conformance runner and reference hygiene also passed.

The L6 jobs ran the pinned 27-case corpus; RI-PY and RI-RS checks, nine negative preservation fixtures, isolated-container checks and report-hash checks all passed on both architectures. The test commands used Docker `--network none`; that is container-level isolation only.

The JSON pilot observed eight candidates through RI-PY and RI-RS: 8 agreements, zero mismatches. **Semantic status remains `CONTRACT_UNRESOLVED`** because expected outcomes are not assigned and the policy is `CONTRACT_DECISION_REQUIRED`. This is not a normative conformance result.

## Target Air-Gap L0 state

**`PREPARED_NOT_EXECUTED`.** The evidence package includes the L0 handoff archive, the expanded handoff scripts, procedure v1.0, and a result template initialized to NOT_EXECUTED. No execution against the intended target’s actual pinned Git checkout has been evidenced in this session. No independent infrastructure/physical isolation attestation has been received.

Pinned target identity:

- Commit: `6b4f3dcc46841bb17fafa3e1b1cc8ea9c0397330`
- Manifest: `fixtures/corpus/STAGE-C-C6-STRICT-WIRE-MUTATION-CORPUS-v0.1-DRAFT.json`
- Git blob OID: `d9b4a1f488185a44f7edb233ef8ff180981f0e84`
- Bytes: `9559`
- SHA-256: `c975cb0a3b02670b63ebb0e2809a2e0cb7c8247c2f0dc1a9829466f4806ea49d`

A source ZIP without `.git` is insufficient. The runner must already contain the required Git object graph. Guest network observations or a container’s `--network none` are not proof of whole-host/physical Air-Gap.

**L0 acceptance nuance:** require saved exit code `0` and exact-line presence `L0_SOURCE_LOCK=PASS` in `l0-run.log`. The wrapper appends timestamps, exit code and Air-Gap caveat lines after this marker, so the marker need not be the literal final log line.

## Required disposition

- Gate remains `BLOCKED_PENDING_EVIDENCE_REVIEW`.
- `authority=NONE`, `authorization_effect=NONE`, `governance_effect=NONE`, `release_effect=NONE`.
- Next action: transfer the handoff through the approved offline process, execute L0 on the intended pre-provisioned target, preserve raw output/checksums, and obtain independent infrastructure/physical isolation review.
- Keep L1/L2, ratification, release and gate promotion outside this L0 procedure. The JSON contract decision also remains unresolved.

This record preserves observed outputs; it does not make any new normative claim or authorize release.
