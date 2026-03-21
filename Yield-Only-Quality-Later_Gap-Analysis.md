"Yield Only, Quality Later" Business Logic Gap Analysis

here are the critical gaps and real-world agricultural marketplace considerations:

### 1. **Quality Verification Gaps**

| Gap | Current Implementation | Real-World Requirement |
|-----|----------------------|------------------------|
| **Re-assessment** | No mechanism to re-assess a harvest | Products may need re-grading if conditions change (storage degradation) |
| **Multi-lot sampling** | Single assessment per harvest | Large harvests should be sampled from multiple lots for accuracy |
| **Timestamp validation** | No expiry on assessment validity | Many markets require assessment within X days of listing |
| **Appeal process** | No way to challenge/appeal a REJECT grade | Farmers should be able to request re-assessment |

### 2. **Lab Provider Integration Gaps**

| Gap | Current Implementation | Real-World Requirement |
|-----|----------------------|------------------------|
| **External lab results** | FK constraint requires lab in `lab_providers` | Integration with external certification labs (ISO 17025 accredited) |
| **Chain of custody** | No tracking of sample handling | Documentation of sample collection, transport, lab handling |
| **Lab certification** | No verification of lab credentials | Display lab accreditation numbers on product listings |
| **Parallel testing** | Internal OR external, not both | Some markets require BOTH internal AND external verification |

### 3. **Batch QC Processing Gaps**

| Gap | Current Implementation | Real-World Requirement |
|-----|----------------------|------------------------|
| **Partial batch acceptance** | All-or-nothing QC | Ability to accept partial lots that pass QC |
| **Blending** | No support for mixing lots | Common practice to blend grades for consistency |
| **Batch splitting** | No support for splitting | Large harvests may need separate batches for different markets |
| **Retention samples** | No sample storage | Regulatory requirement to retain samples for X months |

### 4. **Regulatory Compliance Gaps**

| Gap | Current Implementation | Real-World Requirement |
|-----|----------------------|------------------------|
| **Organic certification** | Not integrated | Need organic cert numbers, inspection dates |
| **Geographic indicators** | No PDO/PGI support | Protected designation of origin tracking |
| **Pesticide残留** | Not tracked | Residue testing results for export |
| **Traceability** | Basic lineage hash | Full farm-to-fork traceability with blockchain |
| **Export compliance** | Not considered | Different countries have different import requirements |

### 5. **Edge Cases Not Addressed**

```python
# Missing scenarios:
- Harvest stored for extended period before assessment
- Quality degrades during storage (re-assessment needed)
- Multiple harvests from same cycle sold separately
- Joint ventures between farms (shared batches)
- Contract farming arrangements with pre-agreed grades
- Emergency harvest (natural disaster) - relaxed requirements
- Coop/shared storage facilities
```

### 6. **Recommended Enhancements**

1. **Assessment Validity Period**: Add `valid_until` date to QualityAssessment
2. **Re-assessment Workflow**: Allow requesting new assessment for REJECT grades
3. **Lab Integration**: Add external lab results integration
4. **Compliance Metadata**: Add fields for organic cert, pesticide tests, etc.
5. **Audit Trail**: Full history of all quality-related actions
