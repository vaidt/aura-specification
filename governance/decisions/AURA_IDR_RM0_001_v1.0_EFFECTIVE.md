# AURA — IMPLEMENTATION DECISION RECORD (RM-0)
Artifact_ID: AURA-IDR-RM0-001-v1.0
Document_Type: IMPLEMENTATION_DECISION_RECORD
Title: Release Control Plane Pre-Release Reference Decoupling
Status: EFFECTIVE
Date: 2026-10-05

## 1. Decision Identification

- **Decision_ID:** AURA-IDR-RM0-001
- **Domain:** RELEASE-MANAGEMENT DOMAIN
- **Target_Repository:** `vaidt/Aura-Release-Management`
- **Conflict_Target:** C-008

## 2. Rationale

The current AURA Release Control Plane (RM-0) enforces a hard-coded specification reference (`refs/tags/M0-BASELINE-v1.0`) in both its JSON schema and Python provenance verifier. 

The protocol version baseline decision (`AURA-IDR-PVER-001`) establishes the normative protocol version as `0.1.0-DRAFT`. Therefore, RM-0 currently imposes an unratified production protocol version as a mandatory condition for any release verification.

Release Control must not impose protocol versions; it must verify the exact baseline declared in a valid release manifest.

## 3. Authorization Scope

This IDR proposes the authorization to modify the Release Control Plane repository (`vaidt/Aura-Release-Management`) to decouple the specification reference.

**Allowed Changes (Implementation Scope):**
- Modify the `release_version` schema pattern to permit SemVer-compatible pre-release identifiers.
- Remove the hard-coded `const` tag requirement (`M0-BASELINE-v1.0`) in the M0 schema.
- Update the Python provenance verifier (`provenance.py`) to accept a manifest-declared specification reference.
- Enforce that the verifier resolves the exact manifest-declared reference against the Git tree and compares it to the declared `commit_sha`.
- Update corresponding test fixtures, assertions, and test harnesses to validate this decoupled logic.

**Prohibited Actions (Strict Boundaries):**
- Changing protocol semantics or the normative specification corpus.
- Ratifying a protocol version.
- Declaring system-wide conformance.
- Promoting a release.
- Changing Authority hierarchy or constitutional rules.

## 4. Execution Pathway

1. **Authorization:** This document must receive a valid Authority signature.
2. **Implementation:** Upon becoming EFFECTIVE, changes must be introduced via a Pull Request (PR) in `vaidt/Aura-Release-Management`.
3. **Verification:** The PR must pass independent schema validation, provenance checks, and regression tests.
4. **Merge:** Only after passing tests may the PR be merged to establish the new RM-0 HEAD.

## 5. Preconditions for Effectiveness

- Valid authority signature is present and verifiable.
- The signer is operating within the competent authority scope.
- The effective date is explicit.

## 6. Authority Binding

- **Issuer_Role:** Chief Architect
- **Issuer_Identity:** Kamil Krasiński
- **Competence_Basis:**
  - `vaidt/Authority/Authority Kamil Krasiński Aura-IDToken.md`
  - `AUTHORITY_BINDING_RECORD_v1.1.md`
- **Effective_Date:** PENDING_SIGNATURE_AND_REGISTRATION
- **Signature_Status:** PENDING

## 7. Status

- **Normative_Effect:** NONE
- **Implementation_Authorization:** PENDING_SIGNATURE
