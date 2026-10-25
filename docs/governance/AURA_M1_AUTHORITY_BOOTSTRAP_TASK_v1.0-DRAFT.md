# AURA M1 Authority Bootstrap — Task Definition

**Document ID:** AURA-M1-AUTHORITY-BOOTSTRAP-v1.0-DRAFT  
**Date:** 2026-10-25  
**Classification:** Governance research / evidence reconciliation  
**Status:** DRAFT — NON-CONSTITUTIVE — NO DECISION EFFECT  
**Baseline:** `vaidt/aura-specification/main@11e512365957cd1367062e379bcd655d24048d96`

## 1. Purpose

Establish the evidence and decision procedure required to identify the competent authority for AURA governance decisions. This task does not itself create, appoint, ratify, or delegate authority. It does not authorize implementation, a gate transition, merge, or release.

## 2. Triggering inconsistency

The current `AURA_M1_CLOSURE_RECORD_v1.0.md` contains two incompatible layers:

- Its prefatory notice is marked **PROPOSED DEPRECATION — NON-CONSTITUTIVE; NOT EFFECTIVE** and says that the reviewed source evidence does not establish the claimed authority continuity and constitutional procedure; competent ratification, registration and independent verification are pending.
- Its body still claims `Status: RATIFIED`, `Ratification_Status: EXECUTED`, `M1_Governance_Gate: CLOSED` and `Authority_Continuity: PROVEN`.

This task records the conflict without choosing which statement has effect. The annotation itself explicitly says that it does not invalidate, revoke, or supersede the record. No reader, implementer, automated workflow, repository administrator or contributor may reconcile the conflict by inference.

## 3. Questions that require primary evidence

### A. Constitutive source

1. What primary artifact establishes the authority model and its scope?
2. What is the provenance, immutable revision, content digest and legal/governance effect of that artifact?
3. Does a controlling instrument define a single decision-maker, a committee, or a threshold of authorized signers?
4. What procedure establishes, registers, limits, revokes, rotates and independently verifies the authority?

### B. Identity and signer competence

1. Which cryptographic identity is bound to which role and which decision scopes?
2. What source establishes the binding, and what independent check validates possession/control and scope?
3. How are `allowed_signers`, signing thresholds, expiry, revocation and key compromise handled?
4. Are GitHub account ownership, code contribution, repository administration or a commit signature being improperly treated as constitutive authority? They must not be treated as such without an explicit controlling source.

### C. Ratification and record conflict

1. What source and procedure support the M1 record's executed-ratification assertions?
2. What evidence supports or contradicts the stated genesis, identity-binding and prior decision records?
3. Which competent body can affirm, suspend, withdraw, supersede or return the M1 determination for more evidence?
4. What new decision record is required, and how will the original artifact remain preserved and verifiable?

## 4. Required work products

- **Evidence inventory:** immutable source references, exact commits, Git blob OIDs, content digests, signing/attestation metadata, provenance and independent verification results.
- **Authority model:** single-authority or multi-signature decision rule; roles/scopes; threshold if applicable; identity binding; registration; revocation/rotation; conflict/abstention; and verification procedure.
- **Contradiction matrix:** each M1 assertion, its source, evidence supporting it, evidence challenging it, and a status of PROVEN / DISPROVEN / INSUFFICIENT EVIDENCE without prematurely assigning normative effect.
- **Decision protocol:** authorized reviewer/body, required evidence package, review criteria, permitted dispositions and controlled status-transition route.
- **Independent verification report:** checks source reachability and integrity; verifies the claimed identity/attestation against the controlling rule; records limitations and exceptions.
- **Immutable decision record schema:** decision ID, competent body/role, authority basis, reviewers and key fingerprints, exact source and artifact hashes, applicable criteria, scope, rationale, exceptions, disposition, signatures/attestations, timestamp and explicit `governance_effect`, `authorization_effect`, and `release_effect`.

## 5. Separation-of-duties requirements

1. The person preparing evidence is not, by preparation alone, the competent approver.
2. Passing CI, merging code, owning a repository or editing a Markdown status field does not confer constitutional authority.
3. The generated technical artifact remains immutable. Any authorized disposition is a separate record that references exact source runs, commits, corpus and artifact digests.
4. A status transition must be derived from that separate verified decision through the controlling procedure; it must never be implemented by rewriting a historical CI output.
5. The task owner must not self-certify the authority model unless the already-proven constitutive rule explicitly authorizes that role to do so.

## 6. Fail-closed exit criteria

This task is not complete until all of the following are satisfied:

- [ ] A controlling primary/constitutive source for decision authority is identified and independently checked.
- [ ] The authority model and decision rule are explicit and verifiable.
- [ ] The source chain and cryptographic identity/permission bindings are independently validated.
- [ ] The contradictory M1 assertions have a disposition issued through the proven competent procedure.
- [ ] The disposition is recorded as a separate, immutable, signed/attested artifact.
- [ ] The historic M1 record, source revision and digest are preserved.
- [ ] The controlled transition procedure and limits of its effect are documented.

Until exit criteria have evidence, preserve the current fail-closed operational state: **M1/G1 BLOCKED / NOT PROVEN; DQ-006 OPEN; CONF-003 PARTIAL; C6 evidence awaits review; release NO-GO.** This sentence records the task's operating assumption and is not a constitutive decision.

## 7. Prohibited shortcuts

- Do not hand-edit `AURA_M1_CLOSURE_RECORD_v1.0.md` to make its status appear internally consistent.
- Do not infer authority from a name, public key, fingerprint, commit, GitHub role, historical self-attestation or account mapping unless the controlling source gives it that effect and independent verification confirms it.
- Do not change `c6_gate_status`, CONF-003, DQ-006, M1 or G1 status as part of this bootstrap task.
- Do not remove Draft or merge PR #8, #45 or #46 on the basis of this task or successful CI alone.
- Do not submit an evidence packet to an unnamed or unverified decision body.

## 8. Disposition

This is an evidence-gathering task definition, not an appointment, authorization, ratification or status determination. Its acceptance can establish that the research package is ready for a competent decision; it cannot substitute for that decision.
