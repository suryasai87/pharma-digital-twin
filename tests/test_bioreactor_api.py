"""
Test suite for Bioreactor API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestBioreactorAPI:
    """Test bioreactor monitoring endpoints"""

    def test_list_bioreactors(self):
        """Test GET /api/v1/bioreactor/list"""
        response = client.get("/api/v1/bioreactor/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "bioreactor_id" in data[0]
        assert "status" in data[0]

    def test_get_sensor_data(self):
        """Test GET /api/v1/bioreactor/{id}/sensors"""
        response = client.get("/api/v1/bioreactor/BR-01/sensors?hours=24")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "temperature" in data[0]
            assert "ph" in data[0]
            assert "dissolved_oxygen" in data[0]

    def test_get_digital_twin(self):
        """Test GET /api/v1/bioreactor/{id}/digital-twin"""
        response = client.get("/api/v1/bioreactor/BR-01/digital-twin")
        assert response.status_code == 200
        data = response.json()
        assert "bioreactor_id" in data
        assert "physical_model" in data
        assert "process_state" in data
        assert "maintenance_history" in data
        assert "predictions" in data

    def test_get_current_status(self):
        """Test GET /api/v1/bioreactor/{id}/current"""
        response = client.get("/api/v1/bioreactor/BR-01/current")
        assert response.status_code == 200
        data = response.json()
        assert "bioreactor_id" in data
        assert "status" in data
        assert "cpps" in data
        assert "cqas" in data

    def test_sensor_data_hours_parameter(self):
        """Test sensor data with different hours parameter"""
        for hours in [1, 24, 72, 168]:
            response = client.get(f"/api/v1/bioreactor/BR-01/sensors?hours={hours}")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_invalid_bioreactor_id(self):
        """Test with non-existent bioreactor ID"""
        # Should still return data (mock data generator creates on-demand)
        response = client.get("/api/v1/bioreactor/INVALID-ID/sensors")
        assert response.status_code == 200


class TestBatchAPI:
    """Test batch quality control endpoints"""

    def test_list_batches(self):
        """Test GET /api/v1/batch/list"""
        response = client.get("/api/v1/batch/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "batch_id" in data[0]
            assert "product" in data[0]
            assert "status" in data[0]

    def test_get_batch_details(self):
        """Test GET /api/v1/batch/{id}"""
        response = client.get("/api/v1/batch/B2024-001")
        assert response.status_code == 200
        data = response.json()
        assert "batch_id" in data
        assert "quality_tests" in data
        assert "process_parameters" in data

    def test_batch_yield_prediction(self):
        """Test GET /api/v1/batch/{id}/yield-prediction"""
        response = client.get("/api/v1/batch/B2024-001/yield-prediction")
        assert response.status_code == 200
        data = response.json()
        assert "predicted_yield_percent" in data
        assert "confidence_interval" in data
        assert "model_version" in data

    def test_yield_trends(self):
        """Test GET /api/v1/batch/analytics/yield-trends"""
        response = client.get("/api/v1/batch/analytics/yield-trends?days=90")
        assert response.status_code == 200
        data = response.json()
        assert "average_yield" in data
        assert "total_batches" in data


class TestEquipmentAPI:
    """Test equipment and predictive maintenance endpoints"""

    def test_list_equipment(self):
        """Test GET /api/v1/equipment/list"""
        response = client.get("/api/v1/equipment/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "equipment_id" in data[0]
            assert "health_score" in data[0]
            assert "status" in data[0]

    def test_get_equipment_health(self):
        """Test GET /api/v1/equipment/{id}/health"""
        response = client.get("/api/v1/equipment/BR-01/health")
        assert response.status_code == 200
        data = response.json()
        assert "health_score" in data
        assert "maintenance_urgency" in data
        assert "recommendations" in data

    def test_maintenance_alerts(self):
        """Test GET /api/v1/equipment/predictive-maintenance/alerts"""
        response = client.get("/api/v1/equipment/predictive-maintenance/alerts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestContaminationAPI:
    """Test contamination detection endpoints"""

    def test_contamination_alerts(self):
        """Test GET /api/v1/contamination/alerts"""
        response = client.get("/api/v1/contamination/alerts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "risk_score" in data[0]
            assert "status" in data[0]

    def test_realtime_risk(self):
        """Test GET /api/v1/contamination/realtime-risk/{id}"""
        response = client.get("/api/v1/contamination/realtime-risk/BR-01")
        assert response.status_code == 200
        data = response.json()
        assert "risk_score" in data
        assert "risk_level" in data
        assert "recommended_action" in data

    def test_contamination_summary(self):
        """Test GET /api/v1/contamination/analytics/summary"""
        response = client.get("/api/v1/contamination/analytics/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_alerts" in data
        assert "risk_distribution" in data


class TestAuditAPI:
    """Test audit trail endpoints (21 CFR Part 11 compliance)"""

    def test_get_audit_logs(self):
        """Test GET /api/v1/audit/logs"""
        response = client.get("/api/v1/audit/logs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "audit_id" in data[0]
            assert "timestamp" in data[0]
            assert "user_name" in data[0]
            assert "action" in data[0]

    def test_entity_audit_trail(self):
        """Test GET /api/v1/audit/entity/{type}/{id}"""
        response = client.get("/api/v1/audit/entity/batch/B2024-001")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_compliance_report(self):
        """Test GET /api/v1/audit/compliance/report"""
        response = client.get("/api/v1/audit/compliance/report")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "regulatory_compliance" in data
        assert "recommendations" in data


class TestEBRAPI:
    """Test Electronic Batch Record endpoints"""

    def test_get_ebr(self):
        """Test GET /api/v1/ebr/{id}/record"""
        response = client.get("/api/v1/ebr/B2024-001/record")
        assert response.status_code == 200
        data = response.json()
        assert "batch_id" in data
        assert "product" in data
        assert "raw_materials" in data
        assert "process_steps" in data
        assert "signatures" in data
        assert "data_integrity" in data

    def test_sign_batch_record(self):
        """Test POST /api/v1/ebr/{id}/sign"""
        payload = {
            "signature_meaning": "Reviewed by",
            "reason": "Batch record review completed"
        }
        response = client.post("/api/v1/ebr/B2024-001/sign", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "signature" in data


class TestHealthEndpoints:
    """Test health and monitoring endpoints"""

    def test_health_check(self):
        """Test GET /health"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_root_endpoint(self):
        """Test GET /"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
