from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
def test_health(): assert c.get("/health").json()["status"]=="ok"
def test_integrations(): assert c.get("/api/v1/integrations").status_code==200
def test_restriction_fails_closed():
    j=c.get("/api/v1/restrictions/test").json()
    assert j["bypass_allowed"] is False
def test_real_lab_target_rejected():
    r=c.post("/api/v1/lab/targets",json={"id":"x","kind":"frp","synthetic":False})
    assert r.status_code==400
def test_synthetic_lab():
    assert c.post("/api/v1/lab/targets",json={"id":"lab1","kind":"financing"}).status_code==200
    assert c.post("/api/v1/lab/experiments/lab1").status_code==200
