# AURA — Target Air-Gap L0 Source Lock Execution Procedure v1.0

**Prepared:** 2026-10-25  
**Mode:** fail-closed, controlled target execution, non-constitutive  
**State:** `NOT_EXECUTED` until an actual target run is evidenced.

## Scope

Run Source Lock L0 only against the intended target’s existing, pre-provisioned Git checkout. This is separate from GitHub Actions. Do not run L1/L2, ratification, release, or gate promotion as part of this procedure.

Separate conclusions:
- `L0_SOURCE_LOCK=PASS`: fixed source objects and manifest checks pass.
- `AIR_GAP=PROVEN`: independent infrastructure/physical isolation evidence is reviewed and accepted.
- Neither conclusion by itself grants governance or release authorization.

## Fixed pins

- Expected `HEAD`: `6b4f3dcc46841bb17fafa3e1b1cc8ea9c0397330`
- Manifest: `fixtures/corpus/STAGE-C-C6-STRICT-WIRE-MUTATION-CORPUS-v0.1-DRAFT.json`
- Git blob OID: `d9b4a1f488185a44f7edb233ef8ff180981f0e84`
- Bytes: `9559`
- SHA-256: `c975cb0a3b02670b63ebb0e2809a2e0cb7c8247c2f0dc1a9829466f4806ea49d`

The target requires a standard checkout with `.git` and the pinned object graph. A GitHub source ZIP without Git metadata is insufficient. Do not clone/fetch, install packages, download Cargo/Python dependencies, or perform other network-dependent steps inside the isolated target.

## Transfer and preflight

1. Identify the target asset and execution operator. Record identity, role, timestamps, transfer custody and required media identifiers; never include credentials.
2. Transfer `AURA_L0_RUNNER_HANDOFF_2026-10-25.zip` using the approved offline process.
3. Verify the published archive SHA-256 and the handoff's internal checksum file on the preparation side and again on target:
   `cd /path/to/AURA_L0_RUNNER_HANDOFF_2026-10-25 && sha256sum -c SHA256SUMS`
4. Enforce the approved isolation control before execution; independently capture infrastructure-control-plane or physical-isolation evidence. Guest observations alone are insufficient.
5. Confirm the pre-provisioned checkout's `HEAD` exactly matches the pinned commit and contains the object database. Do not repair missing objects with network access while isolated.
6. Pick a writable output location separate from the source checkout where practical. If any preflight check fails, stop and preserve the failure record.

## Run

From the verified handoff root, use the actual absolute paths selected by the operator:

```bash
./runner/execute_l0_with_evidence.sh \
  /absolute/path/to/aura-specification-checkout \
  /absolute/path/to/evidence-output
```

Do not edit pinned constants, validator code or expected hashes during the run. Preserve the whole evidence-output directory, including `l0-run.log`, `l0-exit-code.txt`, `runner-metadata.txt`, `network-observation.txt`, `air-gap-status.txt`, `handoff-checksums.log`, `handoff-checksums-exit-code.txt` and `EVIDENCE_SHA256SUMS`.

## L0 pass criteria

All are required:
1. `l0-exit-code.txt` contains exactly `0`.
2. `l0-run.log` contains the exact line `L0_SOURCE_LOCK=PASS`.
3. Handoff checksum exit code is `0` and the checksum log shows checked files as OK.
4. Output matches all pins in the fixed-pin section.
5. The collected evidence checksum file verifies successfully.
6. Independent review confirms the run used the actual pinned Git checkout, not an export ZIP or different checkout.

**Log nuance:** the wrapper appends timestamps, exit-code and Air-Gap caveat lines after the underlying script emits `L0_SOURCE_LOCK=PASS`. Therefore, exact-line presence plus saved exit code and pin checks is the criterion; the PASS marker need not be the final log line.

Any mismatch, absent evidence, non-zero code or checksum failure is FAIL/INCOMPLETE. Preserve failed attempts without overwriting them.

## Independent Air-Gap review

The wrapper intentionally writes `AIR_GAP_STATUS=NOT_PROVEN_BY_GUEST_OBSERVATION_ONLY`. An independent reviewer must verify evidence appropriate to the actual environment, such as signed control-plane policy/state, host/hypervisor enforcement, switch/firewall records or physical isolation/seal evidence with timestamps and asset identity. Use only records that exist and can be independently verified.

Do not infer Air-Gap PASS from `ip route`, `/sys/class/net`, no visible default route, or container `--network none`. Record operator and reviewer separately, with evidence IDs and their review outcome.

## Close-out

1. Do not edit raw logs. Hash and verify the complete output directory.
2. Store the evidence in the approved controlled evidence store with custody metadata.
3. Independently review all pins, logs, exit codes, checksums, custody records and isolation evidence.
4. Record separate outcomes for source lock, Air-Gap proof and overall gate.
5. Do not proceed to L1/L2 or promote the Candidate Lab gate from this L0 result alone.

## Known access blocker

As of 2026-10-25, the connected GitHub API showed zero repository-level self-hosted runners for `vaidt/aura-specification`. This means this session could not dispatch to a registered target runner; it does not prove no independently managed external runner exists. The target L0 run and independent isolation evidence remain outstanding.

Gate: `BLOCKED_PENDING_EVIDENCE_REVIEW`. Authority, authorization, governance and release effects: `NONE`.
