# Scripts

This directory contains tooling scripts for traceability validation and repository maintenance.

## Planned Scripts

| Script | Purpose | Phase | Status |
|--------|---------|-------|--------|
| `check-doc-headers.sh` | Verify all normative documents have required metadata headers | IMMEDIATE | PLANNED |
| `check-ids.sh` | Verify no identifier is reused across INV, CONF, FIX, ADR, RFC | IMMEDIATE | PLANNED |
| `check-traceability.sh` | Verify every INV-xxx has a CONF-xxx; every CONF-xxx has a FIX-xxx | IMMEDIATE | PLANNED |
| `validate-fixtures.sh` | Validate all FIX-xxx JSON files against APS-200 schemas | DEFERRED | BLOCKED |
| `generate-traceability-matrix.py` | Auto-generate TRACEABILITY_MATRIX.md from document metadata | DEFERRED | BLOCKED |

## Status

> **Current plan**: start with repository-structure validators that do not freeze unstable payload contracts; defer schema-bound tooling until APS-200 / APS-300 / APS-500 dependencies are explicitly closed.

## Immediate implementation order

The current safe-first automation order is:

1. `check-doc-headers.sh`
2. `check-ids.sh`
3. `check-traceability.sh`

The following remain intentionally deferred until APS-200 / APS-300 schemas and canonical fixture contracts are stable:

- `validate-fixtures.sh`
- `generate-traceability-matrix.py`

## Immediate Wave Scope

| Script | Minimum scope | Prerequisite | Must not assume |
|--------|---------------|--------------|-----------------|
| `check-doc-headers.sh` | detect missing required document metadata headers and malformed header blocks | stable current document header pattern | approval status or semantic correctness of document bodies |
| `check-ids.sh` | detect duplicate or conflicting `INV` / `CONF` / `FIX` / `ADR` / `RFC` identifiers | existing namespace prefixes remain authoritative | that identifiers imply PASS or closure |
| `check-traceability.sh` | validate structural `INV → CONF` and `CONF → FIX` link presence across registry, conformance docs, and fixture indexes/manifests | current registry and indexes stay machine-readable enough for textual extraction | that fixture presence equals normative readiness or executed evidence |

These scripts should validate repository **structure**, not implementation **conformance**.

## Deferred Wave Gates

| Script | Why blocked now | Unblock condition |
|--------|------------------|-------------------|
| `validate-fixtures.sh` | many fixture payloads remain placeholder, parametric, or registry-dependent | APS-200 schemas, APS-300 Evidence Pack structure, and promoted APS-500 fixtures |
| `generate-traceability-matrix.py` | the matrix still carries maturity judgments and open closure semantics that should not yet be hard-coded into generated output | stable requirement mapping, promoted fixtures, and clearer release-evidence rules |

## Conventions

- All scripts MUST be idempotent
- All scripts MUST exit 0 on success, non-zero on failure
- All scripts MUST print a summary of findings
- Scripts MUST NOT modify specification content
- Scripts MUST distinguish structural completeness from conformance PASS
