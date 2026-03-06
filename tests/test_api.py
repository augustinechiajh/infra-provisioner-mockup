from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Health endpoint should return status 200 healthy"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_invalid_resource_type():
    """Provisioning with an unsupported resource type should return 400"""
    response = client.post("/provision", json={
        "resource_type": "unsupported_resource",
        "name": "test",
        "environment": "dev"
    })
    assert response.status_code == 400
    assert "Unsupported resource type" in response.json()["detail"]

def test_missing_fields():
    """Provisioning with missing required fields should return 422"""
    response = client.post("/provision", json={
        "resource_type": "s3_bucket"
        # Missing name and environment
    })
    assert response.status_code == 422