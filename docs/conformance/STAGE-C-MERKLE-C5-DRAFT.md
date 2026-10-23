# Stage C — C5 Merkle domains, tree shape, and audit proof checks

**Status:** DRAFT · NON-NORMATIVE · NOT RATIFIED  
**Branch:** `experiment/stage-c-merkle-c5-20261023`  
**Depends on:** C4 bounded JCS corpus in specification PR #38  
**Authority / governance / release effect:** NONE

## Purpose

C5 checks the Merkle layer separately from JCS canonicalization. The corpus supplies fixed UTF-8 payloads and pinned SHA-256 digests. It is deliberately not a second JCS test: each payload is hashed as raw bytes so failures can be localized to Merkle domain, tree, or proof logic.

## Scope

- **Leaf domain:** `SHA-256(0x00 || payload)`; 17 fixed leaf digests and an explicit unprefixed contrast.
- **Node domain:** `SHA-256(0x01 || left_digest || right_digest)`; a fixed vector plus unprefixed contrast.
- **Empty tree:** root is `SHA-256(empty)`.
- **Tree shape:** fixed roots for sizes 0 through 17, covering empty/singleton trees, powers of two and non-powers of two. Recursive split uses the largest power of two strictly smaller than size; duplicate-last-leaf behavior is not assumed.
- **Proof construction:** every leaf index for each tree size 1 through 17 gets an audit path, for 153 proofs.
- **Proof verification:** the oracle report records exact sibling digest order and valid proof result; the RI-RS integration target compares each generated path to the oracle list and verifies it against the fixed root.
- **Primitive negative controls:** changed leaf, changed root, changed sibling, wrong index, truncated proof and extra proof element must be rejected. These are Merkle primitive tamper controls, not C6 protocol/adapter negative tests.

## Execution model

The specification-side Python code is an independent reference oracle. The dedicated C5 workflow checks the fixed corpus against that oracle, emits a machine-readable report, then checks out a separately pinned RI-RS test source and runs an integration target against the same corpus and oracle proof report. The RI-RS C5 integration target is ignored by generic test runs unless explicitly enabled by the workflow.

The inspected RI-PY production surface `core/merkle.py::MerkleAttestor.generate_leaf` hashes a canonicalized object as an RFC 6962 leaf. It does not expose a matching production tree-root, audit-path, or proof-verification API. Therefore C5 does **not** claim RI-PY/RI-RS production-path parity for tree construction or proofs. The Python oracle is test code, not RI-PY production code. A parity claim requires an evidenced RI-PY production surface or a separately scoped implementation decision.

## Acceptance criteria

C5 may be reported as technically passed only when all assertions pass:

1. Fixed leaf, node-domain, empty-root and tree-root vectors match.
2. Every RI-RS generated audit path equals the independent oracle path for the same tree size and leaf index.
3. Every valid proof verifies against the fixed root.
4. Mutated, malformed-length, wrong-index and tampered-root controls fail closed.
5. The workflow records checked-out source SHAs, corpus hash, oracle report and test output in an artifact.
6. C6 protocol-level negative tests are not folded into this gate and remain downstream.

Any failure leaves C5 incomplete. Failed assertions must not be waived or relabeled.

## Explicit limits

- Bounded corpus, not certification of every possible tree size or all RFC 6962 implementations.
- Tests the RI-RS Merkle primitives at the exact checked-out commit, not every Aura-Guard runtime path or end-to-end ledger behavior.
- The Python reference is test oracle only, not production RI-PY conformance evidence.
- No production algorithm, serializer, dependency graph, protected branch, governance record, authority record, DQ-006/DQ-002/CONF-003 disposition, or release state is changed by this specification-side gate.
- C6 remains unstarted pending human review of C5 evidence.

**C5 success has no governance ratification, implementation-authorization, conformance-acceptance, or release effect.**
