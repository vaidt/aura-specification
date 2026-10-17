# Governance & Status Index

Short navigation index for root-level governance, ratification, closure, and status-bearing artifacts.

## Reading Rule

When multiple records discuss the same governance or closure topic:

1. use the most recent explicitly referenced **record of reference** below;
2. treat older signed or versioned records as **historical** unless a current record points back to them as governing;
3. treat diagnostic, conflict, errata, and impact-analysis documents as **non-constitutive** unless they explicitly say otherwise.

## Records of Reference

| Topic | Current record of reference | Current reading |
|------|-----------------------------|-----------------|
| Root identity / authority binding | [`AUTHORITY_BINDING_RECORD_v1.1.md`](AUTHORITY_BINDING_RECORD_v1.1.md) | Current authority-binding artifact of record |
| Governance consolidation (M1) | [`AURA_M1_CLOSURE_RECORD_v1.0.md`](AURA_M1_CLOSURE_RECORD_v1.0.md) | Consolidated governance closure record; records executed consolidation of the Wave 1 decisions |
| Wave 1 implementation authorization | [`AURA_IMPLEMENTATION_AUTHORIZATION_WAVE1_v1.2.md`](AURA_IMPLEMENTATION_AUTHORIZATION_WAVE1_v1.2.md) | Executed implementation authorization record |
| DQ-006 closure status | [`closures/DQ-006_CLOSURE_PACKAGE.md`](closures/DQ-006_CLOSURE_PACKAGE.md) | Current DQ-006 status of record: OPEN |

## Historical / Superseded Root Records

These files remain in the repository for traceability and signature preservation, but they should not be read as the latest controlling status on their own.

| Artifact | How to read it now |
|---------|---------------------|
| [`AUTHORITY_BINDING_RECORD.md`](AUTHORITY_BINDING_RECORD.md) | Historical predecessor to `AUTHORITY_BINDING_RECORD_v1.1.md` |
| [`AURA_P008_RATIFICATION_RECORD_v1.0.md`](AURA_P008_RATIFICATION_RECORD_v1.0.md) | Historical standalone decision record; current executed state is reflected through `AURA_M1_CLOSURE_RECORD_v1.0.md` |
| [`AURA_NOT_APPLICABLE_DECISION_RECORD_v1.0.md`](AURA_NOT_APPLICABLE_DECISION_RECORD_v1.0.md) | Historical standalone decision record; current executed state is reflected through `AURA_M1_CLOSURE_RECORD_v1.0.md` |
| [`AURA_ERROR_TAXONOMY_DECISION_RECORD_v1.0.md`](AURA_ERROR_TAXONOMY_DECISION_RECORD_v1.0.md) | Historical standalone decision record; current executed state is reflected through `AURA_M1_CLOSURE_RECORD_v1.0.md` |

## Non-Constitutive / Analysis Records

These artifacts are useful context, but they do not by themselves create approval, ratification, closure, or implementation authority.

| Artifact | Classification |
|---------|----------------|
| [`NOT_APPLICABLE_IMPACT_ANALYSIS_v1.0.md`](NOT_APPLICABLE_IMPACT_ANALYSIS_v1.0.md) | Open decision-gap analysis |
| [`AURA_WAVE1_CONTRACT_CLOSURE_ERRATA_v1.1.md`](AURA_WAVE1_CONTRACT_CLOSURE_ERRATA_v1.1.md) | Technical reconciliation / non-constitutive errata |
| [`AURA_NORMATIVE_CONTRACT_CONFLICT_REGISTER_v1.3.md`](AURA_NORMATIVE_CONTRACT_CONFLICT_REGISTER_v1.3.md) | Proposed conflict register / not effective governance act |
| [`AURA-DOCUMENTATION-NORMALIZATION-AUDIT-v1.md`](AURA-DOCUMENTATION-NORMALIZATION-AUDIT-v1.md) | Diagnostic audit only |
| [`AURA-DOCUMENTATION-NORMALIZATION-CONTROL-REVIEW-v1.md`](AURA-DOCUMENTATION-NORMALIZATION-CONTROL-REVIEW-v1.md) | Controlled analysis only |
| [`governance/AURA-AFI-AEP-001_FOUNDING_INSTRUMENT_AND_AUTHORITY_EVIDENCE_PROCEDURE_v0.1-DRAFT.md`](governance/AURA-AFI-AEP-001_FOUNDING_INSTRUMENT_AND_AUTHORITY_EVIDENCE_PROCEDURE_v0.1-DRAFT.md) | Proposed authority-evidence procedure; non-constitutive and not ratified |
| [`docs/governance/GENESIS_SIGNATURE_VERIFICATION_RECORD.md`](docs/governance/GENESIS_SIGNATURE_VERIFICATION_RECORD.md) | Draft; Git blob SHA-1 `c48445e12d15bdf237ad0be45ba764ae6d8a9f1c`; cryptographic sub-check PASS, G1 remains BLOCKED |
| [`docs/governance/ARTICLE_XIII_CONSTITUTIONAL_AUDIT_OPINION.md`](docs/governance/ARTICLE_XIII_CONSTITUTIONAL_AUDIT_OPINION.md) | Draft; Git blob SHA-1 `7fe4e6a4b2420394b25f9d307b5bcc89cced90b1`; procedural effect NOT ESTABLISHED |
| [`docs/governance/AUTHORITY_BINDING_RECORD_v1.2_ANNEX_DRAFT.md`](docs/governance/AUTHORITY_BINDING_RECORD_v1.2_ANNEX_DRAFT.md) | Draft; Git blob SHA-1 `1cf270df7d3474ab0d34414d9a510bce336466fe`; no authority effect |
| [`docs/governance/scripts/verify_sshsig.py`](docs/governance/scripts/verify_sshsig.py) | Git blob SHA-1 `8f2e36635d4ccb9d3e7f46a0725a2f41736be4c0`; Python diagnostic |
| [`docs/governance/scripts/verify_sshsig.mjs`](docs/governance/scripts/verify_sshsig.mjs) | Git blob SHA-1 `ddea7d37d3465b0d9fdc074d1ec25ef181652a79`; Node.js diagnostic |
