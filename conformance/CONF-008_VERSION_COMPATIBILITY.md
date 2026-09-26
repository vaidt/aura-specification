# CONF-008 — Version Compatibility

**Related Invariant:** INV-009
**Category:** Compatibility
**Status:** DRAFT

## Purpose
Verify that protocol, schema, fixture, and evidence version references are mutually compatible under the approved version-compatibility contract.

## Preconditions
- A version-compatibility matrix exists and is approved for the target protocol release.
- The applicable compatibility fixture is bound to that matrix.
- The implementation can emit the version-bearing artifacts required by APS-200 and APS-300.

## Procedure
1. Resolve the governing compatibility matrix for the protocol version under test.
2. Load the applicable compatibility fixture set for that matrix.
3. Execute the implementation and collect the resulting version-bearing artifacts.
4. Inspect all required version references, including protocol version, schema version, fixture corpus version, and evidence/document bindings.
5. Compare the observed combination against the approved compatibility matrix.
6. Record any missing, ambiguous, or incompatible version references.

## Expected Result
All required version references are present and the observed combination is explicitly permitted by the approved compatibility matrix.

## PASS / FAIL
- **PASS:** every required version reference is present and the observed combination is permitted by the approved matrix.
- **FAIL:** any required version reference is missing, contradictory, or outside the approved compatibility matrix.
- **ERROR:** the governing compatibility matrix or bound compatibility fixture is unresolved, unavailable, or cannot be applied deterministically.

## Evidence
EVID-CORE containing the observed version fields, the resolved compatibility matrix identifier, the fixture identifier, and the evaluation result.

## Traceability
| Field | Value |
|-------|-------|
| Test ID | CONF-008 |
| Invariant | INV-009 |
| Related Fixture | FIX-COMPAT / compatibility fixture set bound to the approved matrix |
| Evidence Type | EVID-CORE |

## Current readiness note
CONF-008 is currently **BLOCKED** in repository planning because DQ-003 version semantics and the bound compatibility fixture are not yet normatively closed.
