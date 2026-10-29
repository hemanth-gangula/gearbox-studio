"""
API tests — verify FastAPI endpoints work correctly.

These tests use the FastAPI TestClient which runs the app in-process
without needing a separate server.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.design import GearboxDesign

client = TestClient(app)


class TestHealth:
    def test_health_endpoint(self):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "available_formats" in data
        assert len(data["available_formats"]) > 0

    def test_root_endpoint(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Gearbox Studio" in resp.json()["service"]


class TestCalculate:
    def test_calculate_default(self):
        design = GearboxDesign()
        resp = client.post("/api/designs/calculate", json=design.model_dump())
        assert resp.status_code == 200
        data = resp.json()
        assert data["input_pitch_diameter"] == 40.0
        assert data["output_pitch_diameter"] == 120.0
        assert data["centre_distance"] == 80.0
        assert data["reduction_ratio"] == 3.0

    def test_calculate_custom(self):
        design = GearboxDesign()
        design.gear_parameters.module = 3.0
        resp = client.post("/api/designs/calculate", json=design.model_dump())
        assert resp.status_code == 200
        data = resp.json()
        assert data["input_pitch_diameter"] == 60.0
        assert data["centre_distance"] == 120.0


class TestValidate:
    def test_validate_default(self):
        design = GearboxDesign()
        resp = client.post("/api/designs/validate", json=design.model_dump())
        assert resp.status_code == 200
        data = resp.json()
        assert "is_valid" in data
        assert "issues" in data
        assert "checks_run" in data

    def test_validate_invalid(self):
        design = GearboxDesign()
        design.gear_parameters.input_teeth = 30
        design.gear_parameters.output_teeth = 10
        resp = client.post("/api/designs/validate", json=design.model_dump())
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_valid"] is False


class TestGenerate:
    """Test the generation endpoint. Note: this runs the full pipeline synchronously."""

    def test_generate_returns_ids(self):
        design = GearboxDesign()
        resp = client.post("/api/designs/generate", json=design.model_dump())
        assert resp.status_code == 200
        data = resp.json()
        assert "design_id" in data
        assert "job_id" in data

    def test_get_job(self):
        design = GearboxDesign()
        resp = client.post("/api/designs/generate", json=design.model_dump())
        job_id = resp.json()["job_id"]
        # Give the job time to start
        import time
        time.sleep(1)
        resp = client.get(f"/api/jobs/{job_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["job_id"] == job_id

    def test_get_nonexistent_job(self):
        resp = client.get("/api/jobs/nonexistent-id")
        assert resp.status_code == 404

    def test_get_nonexistent_design(self):
        resp = client.get("/api/designs/nonexistent-id")
        assert resp.status_code == 404

    def test_get_design_after_generation(self):
        design = GearboxDesign()
        resp = client.post("/api/designs/generate", json=design.model_dump())
        design_id = resp.json()["design_id"]
        resp = client.get(f"/api/designs/{design_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["design_id"] == design_id
        assert data["project_name"] == design.project_info.project_name

    def test_list_designs(self):
        resp = client.get("/api/designs")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_file_not_found(self):
        resp = client.get("/api/designs/fake-id/file/nonexistent.dxf")
        assert resp.status_code == 404
