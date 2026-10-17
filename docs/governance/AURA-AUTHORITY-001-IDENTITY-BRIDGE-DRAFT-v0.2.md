# AURA-AUTHORITY-001 — Genesis Authority and Identity Bridge

**Version:** 0.2-DRAFT  
**Status:** PROPOSED · NON-CONSTITUTIVE · NOT SIGNED · NOT RATIFIED  
**Normative effect:** NONE  
**Preparation date:** 2026-10-17  
**Competent issuer:** NOT ESTABLISHED  
**Effective date:** PENDING  
**Registration commit:** PENDING  
**Signature artifact:** PENDING  
**Independent identity proof:** NOT FOUND / NOT PROVIDED IN THIS REVIEW

> **Critical boundary.** This document cannot establish its own authority, appoint its author as Protocol Custodian, turn GitHub account control into constitutional competence, or authorize ACRA-001, a G1 state transition, or Stage 3. The identity statement below is a template for a human declarant to review, amend, and sign personally. It is not a statement made or verified by the preparer of this draft. No identity continuity or authority transfer is treated as proven until the evidence and independent review gates in this document are completed.

## 1. Purpose and scope

This draft defines a controlled process for testing whether the historical GitHub account `Kamil1230xd`, the current account `vaidt`, a named natural or legal person, and a specified cryptographic key can be linked by independently reviewable evidence.

The intended chain is:

`OBSERVED GENESIS REPOSITORY EVENT → ACCOUNT-CONTROL EVIDENCE → DECLARANT IDENTITY CLAIM → INDEPENDENT IDENTITY / DOMAIN CORROBORATION → CURRENT KEY POSSESSION → COMPETENT PRIMARY AUTHORITY SOURCE → EFFECTIVE APPOINTMENT / DELEGATION → EXACT SCOPE → EFFECTIVE DATE → CONTINUING VALIDITY`

These links answer different questions. Proof of control over a GitHub account is not, by itself, proof of a natural person's civil identity. Proof of domain control is not, by itself, proof of legal identity. A signature over a declaration proves a cryptographic relationship between the signed bytes and a key under the verifier's assumptions; it does not independently prove constitutional competence. The authority chain is not established until every required link has an appropriate evidence source.

## 2. Genesis Source — historical repository fact, not a constitutional grant

### 2.1 Observed candidate

| Field | Observed value |
|---|---|
| Repository | [Kamil1230xd/aura-sign-mvp](https://github.com/Kamil1230xd/aura-sign-mvp) |
| Repository creation timestamp | `2025-11-10T18:17:46Z` |
| Candidate root commit | [`d54abf86528fc3785e5c4f8b0c9168d3a7151843`](https://github.com/Kamil1230xd/aura-sign-mvp/commit/d54abf86528fc3785e5c4f8b0c9168d3a7151843) |
| Commit message | `Add package.json` |
| Commit timestamp | `2025-11-10T18:17:47Z` |
| Commit author / committer label | `Kamil1230xd` |
| Parent commits | None (`parents: []`) |
| GitHub signature verification | `verified: false`, reason `unsigned` |

### 2.2 Permitted inference

This commit is an observed parentless root object in the Git history examined for this repository. It is a candidate marker for the beginning of the repository's recorded history.

It must **not** be described as the unique or legally decisive Genesis Source for AURA without additional evidence. It does not establish that this was the first AURA-related project record, prove the real-world identity of the operator of the account, prove legal ownership of all AURA intellectual property, or create constitutional authority. The commit is unsigned; its author label and repository account metadata are not a cryptographic signature by the asserted person.

**Finding:** `ROOT COMMIT IDENTIFIED; CRYPTOGRAPHIC AUTHORSHIP NOT ESTABLISHED BY THIS COMMIT; CONSTITUTIONAL AUTHORITY NOT ESTABLISHED.`

## 3. Attestation of Origin — claimant statement, not an established fact

### 3.1 Declarant must complete this section personally

No value may be inferred or filled by an automated agent. The declarant must verify the statement's accuracy, provide a legally appropriate identity designation, and sign the exact final bytes from a controlled environment.

- **Declarant's full name / legal entity:** `[PENDING — TO BE COMPLETED BY DECLARANT]`
- **Capacity in which the declarant speaks:** `[PENDING]`
- **Historical account:** `Kamil1230xd`
- **Current account:** `vaidt`
- **Identity reference or independent channel:** `[PENDING]`
- **Date of attestation:** `[PENDING]`

### 3.2 Proposed text for personal attestation

> I, **[full name / legal entity]**, make the following first-person declaration, subject to independent verification:
>
> 1. I assert that I personally controlled or was duly authorized to operate the GitHub account `Kamil1230xd` during the relevant period associated with the creation of `Kamil1230xd/aura-sign-mvp`.
> 2. I assert that I presently control or am duly authorized to operate the GitHub account `vaidt`.
> 3. I assert that the two account relationships refer to the same natural person or to a documented legal-entity succession / delegation described in attached evidence: **[specify which, and attach source]**.
> 4. I identify the root commit `d54abf86528fc3785e5c4f8b0c9168d3a7151843` as a historical repository event relevant to this claim, not as a standalone legal grant of constitutional authority.
> 5. I disclose that the identified root commit is unsigned and do not represent its author field as a cryptographic identity proof.
> 6. I request independent verification of the account-control continuity, identity binding, key possession, and any separate primary source that may establish governance competence.
>
> **Declarant signature:** `[PENDING — MUST BE CREATED BY DECLARANT]`  
> **Signature scheme / key fingerprint:** `[PENDING]`  
> **SHA-256 of exact signed content:** `[PENDING]`  
> **Independent verification result and reviewer:** `[PENDING]`

This attestation, even when signed, is a first-person identity/continuity claim. It must not be re-described as independently verified solely because it is cryptographically signed or committed to Git.

## 4. Identity Bridge — evidence required

### 4.1 Historical and current account control

The bridge must distinguish current control from historical control. A new post today under both accounts can support current control of those accounts at the time of verification; it cannot by itself prove who controlled an account at the 2025 Genesis timestamp.

Evidence to gather and preserve in raw form where possible, with retrieval time, URLs, object IDs, hashes, and limits, includes:

- a challenge statement containing a high-entropy nonce published from each account under examination, with exact same statement or mutually linked digests;
- detached signatures over the same canonical challenge from keys whose binding to each account is independently demonstrated;
- historical account records or independently archived evidence relevant to control at the stated time;
- platform-origin evidence that independently links the accounts to a person or documented legal entity;
- corroboration through a domain or identity channel not controlled solely by the disputed key.

A nonce must be generated at execution time, included in the evidence package, and checked for reuse. Do not invent or pre-fill a nonce in this draft.

### 4.2 Public-key binding and key transition

An existing AURA record declares the following key. Its appearance here identifies an existing declaration; it does not independently verify the identity or prove competence:

```text
Key type: ssh-ed25519
Fingerprint: SHA256:u9HaNYWZGQYvGET5ZaX2c/V56MzL0Xo7Ilg9M1pZRwU
Public key: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPtUzzZnVuXqd+HixKurmhIELs1RGO6He1nS/dOY80X4 genesis-aura
Source: AUTHORITY_BINDING_RECORD_v1.1.md
```

- **Proposed new Protocol Custodian key:** `PENDING — DO NOT INVENT OR ASSUME`
- **New-key fingerprint:** `PENDING`
- **Proof of current possession:** `PENDING`
- **Revocation / compromise status:** `PENDING`
- **Key validity interval and intended namespace:** `PENDING`

A Trust Transfer must be treated as a proposed key-rotation / identity-binding event, not as an automatic transfer of constitutional power. It must identify the old and new key fingerprints, the declarant, the canonical challenge or content digest, the effective time, the revocation behavior, and the independent verifier. If the old key is not available or its relationship to the historical account is not established, this limitation must be recorded rather than papered over.

## 5. External corroboration — proposed methods and limits

No independently verified public DNS TXT record, Keybase proof, domain control statement, or public identity bridge linking `Kamil1230xd`, `vaidt`, the named declarant, and a new key was provided or verified during this review. This is a statement about the evidence examined, not proof that no such record exists.

The following channels may be considered, if controlled by the declarant and independently verified:

1. **DNS TXT:** publish a challenge-bearing record under a project domain, such as `_aura-authority.<controlled-domain>`, binding the exact canonical declaration digest and nonce to the named accounts and key fingerprint.
2. **HTTPS well-known record:** publish the same challenge and digest at a stable path such as `/.well-known/aura-identity-bridge.txt` under a controlled domain.
3. **Public account proofs:** publish mutually linked, challenge-bound statements from the two GitHub accounts and retain the original URLs and timestamps.
4. **Keybase or another identity service:** link it only after a live proof is located and its verification status is independently read back.

A DNS/HTTPS proof can demonstrate control of the domain or hosting origin at the verification time. A profile or repository post can demonstrate control of that account at the time observed. Neither alone establishes civil identity, historical account control at the root-commit time, ownership of the protocol, or constitutional competence. Stronger identity assurance requires corroborating evidence from a channel whose trust basis is not circularly derived from the disputed key or repository.

## 6. Authority source and proposed role scope

### 6.1 Mandatory authority chain

| Gate | Required evidence | Status |
|---|---|---|
| AB-01 — Primary source | Pre-existing charter, agreement, resolution, constitution, or other competent instrument that establishes authority | **NOT ESTABLISHED** |
| AB-02 — Issuer competence | Evidence that the source instrument's issuer was competent to grant the asserted authority | **NOT ESTABLISHED** |
| AB-03 — Identity bridge | Attestation and independent evidence linking the relevant person/entity, accounts, and keys | **NOT ESTABLISHED** |
| AB-04 — Appointment / succession | Effective appointment, succession, or delegation under the established source | **NOT ESTABLISHED** |
| AB-05 — Scope | Exact roles, repositories, decisions, limits, conflicts, and conditions | **PROPOSED ONLY** |
| AB-06 — Time / validity | Effective date, current validity, expiry, suspension, and revocation terms | **NOT ESTABLISHED** |
| AB-07 — Independent review | Attributable review of the full source chain and conflicting records | **PENDING** |
| AB-08 — Ratification and registration | Competent decision, exact signed digest, signature verification, effective date, and registration evidence | **PENDING** |

### 6.2 Proposed role scope — not granted by this draft

Only after AB-01 through AB-08 are independently satisfied may a competent issuer consider a separate appointment that defines whether the role of Protocol Custodian has power to:

- review and, if competent under the established source, ratify a crisis-resolution act such as AURA-ACT-001;
- issue a governance-gate determination for G1 within a defined scope;
- authorize a specific Stage 3 design or implementation act, subject to separate gates;
- register the exact decision revision, digest, effective date, limitations, and revocation conditions.

The powers above are **proposals for a future competent decision**, not delegations made by this file. This draft must not become its own primary source of authority. Any role must also preserve independent review requirements and conflict-of-interest controls; role assignment does not automatically waive those safeguards.

## 7. Relationship to ACRA-001, AURA-CRA-001, and the observed repository state

- [PR #33 — AURA-CRA-001](https://github.com/vaidt/aura-specification/pull/33) has a recorded administrative comment stating `SUPERSEDED`, but GitHub metadata currently reports the PR as merged at `2026-10-17T19:24:41Z`, merge commit `b43ae9073344c936baa6d8b4bb60ff9fc9b268b7`.
- [PR #34 — AURA-ACT-001 / ACRA-001](https://github.com/vaidt/aura-specification/pull/34) is also reported as merged at `2026-10-17T19:24:59Z`, merge commit `16b1ba1f18a37f9cfeba6bf777bd7439d71b8b48`.
- Both documents on `main` still declare `PROPOSED · NON-CONSTITUTIVE · NOT RATIFIED`.

The administrative `SUPERSEDED` comment and the observed merge metadata for PR #33 conflict. This draft records that discrepancy; it does not silently declare the conflict resolved or choose a canonical Act identifier. A competent, independently reviewed decision must determine the future relationship of both drafts before either can be treated as the unique effective proposal.

Until the authority chain is independently established:

- `AURA-ACT-001 / ACRA-001` remains `PROPOSED · NON-CONSTITUTIVE · NOT RATIFIED`;
- proposed deprecation of `AURA_M1_CLOSURE_RECORD_v1.0.md` remains `PROPOSED · NOT EFFECTIVE`;
- `G1 = NOT PROVEN / BLOCKED` for new decisions relying on the disputed authority chain;
- `AURA-STAGE3-AUTH-001 = PROPOSED / NOT AUTHORIZED`;
- no runtime implementation, normative change, conformance claim, or release authorization follows from this draft.

The conflicting historical M1 record must be preserved. Any future status reconciliation requires a competent decision, a preserved link to the original record, an effective date, and independently verified registration evidence.

## 8. Signature, registration, and verification — intentionally pending

- Exact final document revision: `PENDING`
- SHA-256 of exact approved document bytes: `PENDING`
- Declarant full identity and capacity: `PENDING — DECLARANT TO COMPLETE`
- Identity Bridge challenge / nonce: `PENDING — GENERATE AT EXECUTION`
- Old-account control evidence: `PENDING`
- Current-account control evidence: `PENDING`
- Independent identity / domain corroboration: `PENDING`
- New public key and fingerprint: `PENDING`
- Signature file or transparency-log reference: `PENDING`
- Signature scheme, namespace, and verification result: `PENDING`
- Key validity and revocation review: `PENDING`
- Primary authority source and issuer competence: `NOT ESTABLISHED`
- Independent reviewer and report: `PENDING`
- Decision record, registration commit, and effective date: `PENDING`

The private key must never be supplied to an assistant, committed to Git, or stored in a repository as plaintext. The declarant must create any eventual signature in a controlled environment; a reviewer must then verify the exact bytes and record the verification result independently.

---

**Current determination:** `ROOT COMMIT IDENTIFIED; IDENTITY CONTINUITY NOT PROVEN; AUTHORITY CONTINUITY NOT ESTABLISHED.`  
**Document status:** `PROPOSED · NON-CONSTITUTIVE · NOT SIGNED · NOT RATIFIED.`
