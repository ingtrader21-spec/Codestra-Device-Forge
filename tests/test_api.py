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
def test_dashboard(): assert c.get("/").status_code==200
def test_os_catalog(): assert c.get("/api/v1/catalog/os").status_code==200
def test_app_catalog(): assert c.get("/api/v1/catalog/apps").status_code==200

def test_devices_never_promotes_apple_error_text(monkeypatch):
    import app.adapters as a
    monkeypatch.setattr(a, "run_readonly", lambda tool,args,timeout=8: {"available": True, "returncode": 1, "output": "ERROR: Unable to retrieve device list!"})
    assert a.discover_apple() == []

def test_provider_health_endpoint():
    r=c.get("/api/v1/providers")
    assert r.status_code==200
    ids={x["id"] for x in r.json()}
    assert "openeuicc" in ids

def test_openeuicc_status_endpoint():
    r=c.get("/api/v1/esim/providers/openeuicc")
    assert r.status_code==200
    assert r.json()["provider"]=="openeuicc"

def test_jobs_are_approval_gated():
    r=c.post("/api/v1/jobs",json={"kind":"diagnostic","requires_approval":True})
    assert r.status_code==200
    j=r.json()
    assert j["state"]=="AWAITING_APPROVAL"
    a=c.post(f"/api/v1/jobs/{j['id']}/approve")
    assert a.status_code==200
    assert a.json()["state"]=="READY"

def test_registry_endpoint():
    assert c.get("/api/v1/devices/registry").status_code==200
