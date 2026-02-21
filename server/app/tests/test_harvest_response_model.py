from app.api.v1.harvest.schemas import ProductConversionResponse


def test_product_conversion_response_accepts_sample_dict():
    sample = {
        "id": "prod-uuid",
        "name": "Sample Product",
        "total_quantity": "100",
        "status": "converted",
        "is_active": False,
        "product_batches": [
            {
                "id": "pb-uuid",
                "batch_code": "PB-001",
                "total_quantity": "100",
                "quality_grade": None,
                "links": [
                    {
                        "harvest_batch_id": "hb-uuid",
                        "batch_code": "BATCH-1",
                        "status": "QC_PASSED",
                        "lineage_hash": "abcd",
                        "aggregated_weight_kg": 100.0,
                        "moisture_avg": 12.3,
                        "qc_reports": [
                            {
                                "id": "qc-1",
                                "lab_id": "LAB-1",
                                "tested_at": "2026-02-20T10:00:00Z",
                                "metrics": {"moisture": 12.3},
                                "passed": True,
                                "report_url": None,
                                "verified": True,
                            }
                        ],
                        "contribution_weight_kg": 100.0,
                    }
                ],
            }
        ],
        "harvest_batch_id": "hb-uuid",
        "harvest_batch_status": "QC_PASSED",
        "harvest_batch_lineage_hash": "abcd",
        "harvest_batch_aggregated_weight_kg": 100.0,
        "qc_status": "PASSED",
        "qc_lab_id": "LAB-1",
        "qc_tested_at": "2026-02-20T10:00:00Z",
    }

    # Should not raise
    resp = ProductConversionResponse.parse_obj(sample)
    assert resp.id == "prod-uuid"
    assert resp.product_batches and resp.product_batches[0].id == "pb-uuid"
