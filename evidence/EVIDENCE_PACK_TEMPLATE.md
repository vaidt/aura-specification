# Evidence Pack Template

Use this template to document an Evidence Pack. All fields marked MUST are required by APS-300.

---

## Evidence Pack Metadata

| Field | Value |
|-------|-------|
| Pack ID | `[UUID v4]` |
| Protocol Version | `[APS version, e.g., 1.0]` |
| Schema Version | `[APS-300 schema version]` |
| Implementation ID | `[e.g., RI-PY, RI-RS]` |
| Execution ID | `[UUID v4 from Protocol Header ENT-001]` |
| Generated At | `[ISO 8601 UTC timestamp]` |

---

## Components

### 1. Evidence Object (MUST — APS-300 §5)

```json
{
  "evidence_id": "TODO",
  "protocol_version": "TODO",
  "schema_version": "TODO",
  "implementation_id": "TODO",
  "execution_id": "TODO",
  "timestamp": "TODO",
  "policy_reference": "TODO",
  "input_hash": "TODO — SHA-256",
  "output_hash": "TODO — SHA-256",
  "evidence_hash": "TODO — SHA-256",
  "previous_evidence_hash": "TODO — SHA-256 or null",
  "attestation_reference": "TODO"
}
```

### 2. Evaluation Result (MUST — ENT-003)

> Include the full Evaluation Result object per APS-200 ENT-003. The draft machine-readable top-level schema lives at `fixtures/schemas/evaluation-result.schema.json`.

### 3. Policy Reference (MUST — ENT-004)

> Include the full Policy Reference object per APS-200 ENT-004. The draft machine-readable top-level schema lives at `fixtures/schemas/policy-reference.schema.json`.

### 4. Attestation (MUST — ENT-006)

> Include the full Attestation object per APS-200 ENT-006. The draft machine-readable top-level schema lives at `fixtures/schemas/attestation.schema.json`.

### 5. Integrity Metadata (MUST)

> **TODO**: Define the final Integrity Metadata vocabulary. Until then, include at minimum SHA-256 of each component plus SHA-256 of the full pack.

---

## Verification Checklist

- [ ] All mandatory Evidence Object fields present
- [ ] evidence_hash independently verified
- [ ] input_hash matches canonical input
- [ ] output_hash matches canonical output
- [ ] attestation_reference resolves to valid Attestation
- [ ] All component objects pass APS-200 schema validation
- [ ] Evidence Pack sealed (hash of all components computed and stored)
