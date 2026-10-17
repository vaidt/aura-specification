# Article XIII Constitutional Audit Opinion

**Document ID:** AURA-AXIII-AUDIT-001  
**Version:** 0.1-DRAFT  
**Status:** DRAFT · NON-CONSTITUTIVE · NOT RATIFIED  
**Normative effect:** NONE  
**Review date:** 2026-10-17  
**Repository baseline:** `vaidt/aura-specification@8f0cd6be94a68a3728e69a1d21d49237c9d8bd05`

> This is a source-based internal governance audit, not an external legal opinion. It does not enact, invalidate, ratify, or repeal Article XIII and does not decide any matter of applicable external law.

## 1. Question and disposition

**Question:** Does the reviewed repository evidence establish that Article XIII entered into force through the applicable constitutional procedure, that Genesis Authority validly appointed the initial Chief Architect, and that this authority chain currently supports ratification of `AURA-STAGE3-AUTH-001`?

**Disposition:** **PROCEDURAL EFFECT NOT ESTABLISHED FROM THE SOURCES REVIEWED. G1 REMAINS BLOCKED.**

This is not a final declaration of legal invalidity. It means the available source set does not prove the necessary chain of authority and procedural effectiveness. A favourable status label in a later record cannot resolve the source conflict by itself.

## 2. Frozen constitutional baseline and insertion of Article XIII

### 2.1 Baseline before insertion

The parent revision examined for the Article XIII insertion is `865b0d68b2f566759f096e1b7a5c67b5ed4f858b`. The Constitution at that revision states:
- `Document ID: AURA-CON-001`
- `Version: 1.0`
- `Status: FROZEN`
- the document's content is immutable once frozen and amendments require a new version under Article XI.

The parent text includes Articles I–XII and does **not** include Article XIII.

### 2.2 Insertion commit

Commit [`a53ef122f9cedbf110f30ed57ddd7ef1db6f1491`](https://github.com/vaidt/aura-specification/commit/a53ef122f9cedbf110f30ed57ddd7ef1db6f1491):
- is dated `2026-09-21T19:32:53Z`;
- changes `constitution/AURA_CONSTITUTION.md` by adding four lines for Article XIII;
- leaves the document header at Version 1.0 and Status FROZEN;
- does not include a constitution version bump or, in the commit itself, an RFC, Architecture Review, impact analysis, dependent-document updates, or approval record required by Article XI;
- is reported by GitHub as a valid signed Git commit; that proves a verified commit signature for the commit object, not completion of the constitutional amendment process.
- returned an empty list from the reviewed GitHub associated-pull-requests endpoint.

The file blob after insertion is `ae121ce247066fb2cc920fb7114e6547fd4f7398`.

### 2.3 Article XI requirements

Article XI expressly states that constitutional amendment requires:
1. an RFC;
2. an Architecture Review;
3. an impact analysis;
4. updates to dependent documents; and
5. approval by the Chief Architect.

It also states that a frozen version is immutable. The Article XIII insertion changed the already frozen v1.0 file without changing its declared version. The reviewed source set does not establish that the listed amendment steps were completed before or as part of this insertion. The requirement is therefore **NOT ESTABLISHED**, not presumed satisfied.

A repository search at the observed main revision did not find a source artifact that clearly acts as an RFC/Architecture Review/impact analysis specifically approving this Article XIII insertion. An unrelated RFC or impact analysis cannot be attributed to the Article XIII amendment without explicit binding evidence.

## 3. Text of Article XIII and the self-authorisation question

Article XIII says, in substance, that if the Chief Architect role is vacant before full launch (M1/G0), the Original Creator and Genesis Owner possessing proven cryptographic control over the canonical repository has exclusive meta-constitutional authority to appoint the initial Chief Architect, bypassing Article XI.

This text purports to create a scoped appointment mechanism and uses self-executing language (“shall hold”, “shall be final”). It does not expressly require an external ratification of each appointment. However:
- the prerequisites—vacancy, recognised status as Original Creator/Genesis Owner, and proven control over the canonical repository—still require evidence;
- the presence of this text in a repository file does not, by itself, establish that the amendment inserting it was validly adopted;
- Article XIII cannot be treated as conclusive proof of its own valid enactment when the act of inserting Article XIII is precisely what remains procedurally unproven;
- even a valid appointment clause would not automatically establish the exact current scope, duration, and limits of every later decision power without interpreting the actual wording and any other governing constraints.

The evidence does not conclusively establish whether the intention was for Article XIII to operate as an immediately effective internal rule or whether an additional prior authority instrument was required. It does establish that the repository evidence reviewed here is insufficient to bypass the unresolved amendment-procedure question.

## 4. Genesis declaration, appointment, and identity chain

The exact declaration `GENESIS_DECLARATION.txt` states:
- date: `2026-09-24`;
- place: `Ilawa, Poland`;
- the signer claims to be the Original Creator;
- the signer claims to convert technical ownership into constitutional Genesis Authority;
- the signer declares Article XIII enacted, appoints Kamil Krasiński initial Chief Architect, and grants broad authority to ratify protocol changes and authorise implementations.

The declaration's preimage SHA-256 is `6b5a4c4eaa258eef27452fe6a2f2d752484ae6c88968a039b0b40ca0ac8f2bb6`. Its detached SSHSIG verifies cryptographically against the public key with fingerprint `SHA256:u9HaNYWZGQYvGET5ZaX2c/V56MzL0Xo7Ilg9M1pZRwU`; see [Genesis Signature Verification Record](GENESIS_SIGNATURE_VERIFICATION_RECORD.md).

These results support the integrity and cryptographic origin of the declaration under that key. They do **not** independently establish:
- the real-world identity of the person who controlled the private key when the declaration was signed;
- that the person qualified as the “Original Creator and Genesis Owner” under a previously effective governance rule;
- exclusive or unencumbered legal authority to convert technical repo ownership into constitutional authority;
- the absence of a prior agreement, co-owner, organisation, or other instrument limiting the asserted authority;
- that Article XIII had been validly adopted before the declaration attempted to enact it;
- the real-world legal status or effect of the appointment.

### 4.1 Repository history and chain-of-title limits

The GitHub repository metadata reviewed shows:
- `Kamil1230xd/aura-sign-mvp` was created `2025-11-10T18:17:46Z`. It has verified GitHub commit signatures in December 2025, including commit `2631101c9aa4971b8fe635b08666fbcadb658496` (2025-12-15).
- `Aura-IDToken/aura-poc-a-core-v3.3` was created `2026-01-04T13:31:58Z`; the API query for commits before 2026-01-01 returned no commits, and the earliest reviewed January history includes activity by the `Aura-IDToken` account and Copilot.
- These repo metadata, owner handles and GitHub commit-signature states are evidence of platform-level ownership/history. The inspected records do not cryptographically bind a historical repo-owner account, its GitHub commit-signing key, or historical control of the canonical repository to the same natural person holding the Genesis Ed25519 private key.

The phrase in the Genesis declaration referring to the listed repositories “since January 2026” needs precise interpretation because `aura-sign-mvp` predates January 2026. This chronology discrepancy does not disprove authorship, but it means the wording alone is not a sufficient origin or exclusivity proof.

A technical ability to create or administer a repository is not, without a prior applicable rule or instrument, proof of exclusive constitutional competence.

## 5. Authority Binding v1.1 and M1 closure reconciliation

### 5.1 Cryptographic relationship

The detached signature for `AUTHORITY_BINDING_RECORD_v1.1.md` also verifies in Python, OpenSSL and Node.js. Its namespace is `aura-governance` and its embedded key fingerprint is the same as the Genesis signature. Its document SHA-256 is `9544bee7bb3a042cac5041deb73706832c04c5d0e83f5c01252c71e839e678f0`.

This establishes that the same cryptographic key signed the two artefacts. It does not independently attest that the key holder's self-declared real-world identity or constitutional authority is true. The record and signature use the same root key that the record purports to bind, so the evidence is internally consistent but not an independent identity or competence source.

### 5.2 M1 closure claim

`AURA_M1_CLOSURE_RECORD_v1.0.md` reports:
- `Status: RATIFIED`;
- `Ratification_Status: EXECUTED`;
- `Authority_Continuity: PROVEN`;
- `M1_Governance_Gate: CLOSED`.

The current Article XIII source-review record, meanwhile, says `PROCEDURAL EFFECT NOT ESTABLISHED FROM THE SOURCES REVIEWED`. The present signature verification corrects its narrow claim that the SSHSIG algorithm field reads `sshoed25519`; the exact current signature field is `ssh-ed25519` and the mathematical signature check passes. This correction does not remedy the Article XI procedure gap or the identity/competence gap.

The M1 closure record is a source-of-record declaration, but its conclusion is not independently substantiated by the evidence gaps described here. The conflict requires an explicit, reasoned reconciliation by a competent human authority after the underlying primary evidence has been supplied. Choosing the M1 label as the sole tiebreaker would be circular.

### 5.3 Scope of Wave 1

`AURA_IMPLEMENTATION_AUTHORIZATION_WAVE1_v1.2.md` is limited to `vaidt/aura-specification`, a specified baseline, and named paths. It explicitly excludes other implementation repositories. It cannot, by analogy, authorise Stage 3 design in `vaidt/Kt-ry-Program` or implementation repositories.

## 6. Findings matrix

| Vector | Observed finding | Status |
|---|---|---|
| Declaration preimage integrity | Exact repository blob and SHA-256 reproduced | PASS |
| Detached Genesis signature | Ed25519 math passes across Python, OpenSSL and Node; canonical OpenSSH CLI run unavailable | CRYPTOGRAPHIC SUB-CHECK PASS / CLI INTEROP NOT RUN |
| Genesis key vs Authority Binding key | Same SSH public-key fingerprint in both artefacts | PASS — internal key continuity only |
| Signature creation date | SSHSIG carries no timestamp; commit timestamps are not signature timestamps | NOT ESTABLISHED |
| Key revocation | No revocation register/list found in reviewed source set | NOT ESTABLISHED |
| Original creator / Genesis Owner identity | Account history exists, but no independent binding to the Genesis private key or source grant | NOT PROVEN |
| Exclusive competence to establish Genesis authority | No prior constitutive source establishing this conversion was identified in reviewed set | NOT PROVEN |
| Article XIII adoption procedure | Frozen v1.0 changed; version not incremented; Article XI evidence not found bound to insertion | NOT ESTABLISHED |
| Appointment effectiveness | Depends on unresolved Article XIII enactment and identity/competence prerequisites | NOT ESTABLISHED |
| M1 closure consistency | Closure claims conflict with unresolved source-level procedure and authority findings | UNRESOLVED |
| Authority for `AURA-STAGE3-AUTH-001` | No independently established current competence for the exact act | G1 BLOCKED |

## 7. Required evidence to revisit G1

Before G1 can pass, the evidence package must include, at minimum:

1. A primary source predating the Genesis declaration that establishes who could found or control the AURA constitutional governance and the scope of that power.
2. Evidence of the source issuer's competence and the applicable rule or instrument, including the real-world legal/organisational form if an external legal claim is intended.
3. Independently reviewable evidence linking the identity and relevant historical repository control to the holder of the Genesis key; GitHub ownership and a self-signed binding record alone are insufficient.
4. Evidence that the Chief Architect role was in the stated vacancy condition at the relevant date, or a reasoned disposition if that fact is disputed.
5. Evidence satisfying Article XI for insertion of Article XIII, or a competent decision grounded in a previously effective source showing why Article XI did not govern the insertion.
6. A reconciliation decision addressing the M1 closure claim, the Article XIII source review, and the corrected signature-format observation.
7. Any applicable external agreements/consents or a documented finding, supported by evidence, that no such instrument restricts the proposed competence.
8. A separate, exact-scope ratification of `AURA-STAGE3-AUTH-001` after G1 passes.

## 8. Final disposition

**Article XIII procedural effectiveness:** NOT ESTABLISHED FROM THE SOURCES REVIEWED.  
**Genesis signature mathematics:** PASS, with canonical OpenSSH CLI interoperability still to be run.  
**Identity and source of constitutional competence:** NOT PROVEN.  
**M1 reconciliation:** OPEN.  
**G1:** BLOCKED.  
**`AURA-STAGE3-AUTH-001`:** remains a proposal; effective authorization remains `NOT AUTHORIZED`.

This draft does not mark Article XIII invalid as a matter of external law, does not ratify any record, and does not authorise implementation. Any transition to an effective state requires a competent human decision grounded in constitutive evidence and registered through the applicable procedure.
