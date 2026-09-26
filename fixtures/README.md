# Fixtures

This directory contains Reference Fixtures as defined in APS-500.

## Directory Structure

```
fixtures/
├── README.md               This file
├── ck003/                  CK-003 manifests and expected digests
├── corpus/                 Working fixture corpus for open closure items
├── schemas/                JSON Schema definitions for APS-200 entities
├── core/                   FIX-CORE — baseline operation scenarios
└── ...                     Additional APS-500 categories added as they are stabilized
```

## Status

> **Current state**: The canonical APS-500 fixture corpus is not yet finalized. `FIX-001` remains a placeholder, while `/fixtures/corpus/` and `/fixtures/ck003/` contain working fixtures and manifests for closure work that do not by themselves constitute release-ready APS-500 coverage.

## Fixture Index

| Fixture ID | Name | Category | CONF Test | Status |
|------------|------|----------|-----------|--------|
| FIX-001 | Basic Evaluation | CORE | CONF-001 | TODO |
| FIX-INV-007 | Zero Float Runtime | CORPUS | CONF-011 | READY (working corpus) |
| FIX-INV-012 | Event Type / Auditability | CORPUS | CONF-012 | REGISTRY_DEPENDENT |
| FIX-INV-013 | Policy Determinism | CORPUS | CONF-013 | PARAMETRIC |
| FIX-INV-014 | APS-500 Compatibility | CORPUS | CONF-014 | APS500_VERSION_BLOCKED |
| FIX-INV-015 | Canonical Identity | CORPUS | CONF-015 | APS000_BINDING_BLOCKED |

## Authoring New Fixtures

1. Copy [`../templates/FIXTURE_TEMPLATE.json`](../templates/FIXTURE_TEMPLATE.json)
2. Assign the next sequential `FIX-NNN` identifier
3. Place in the appropriate category subdirectory
4. Link to related CONF-xxx test(s) and INV-xxx invariants
5. Submit via pull request with a reference to the related APS-500 section

Working corpus fixtures in `/fixtures/corpus/` MAY evolve during closure work; only fixtures promoted into the approved APS-500 corpus are normative.

## Important Rules

- Fixture IDs are NEVER reused
- A fixture whose Expected Output changes becomes a NEW fixture (new ID)
- Old fixtures are deprecated, not modified
- Fixtures MUST be used unmodified by implementations
