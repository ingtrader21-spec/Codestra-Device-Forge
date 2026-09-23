from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from .adapters import integrations, discover_android, discover_apple
from .models import LabTarget

app=FastAPI(title="Codestra Device Forge",version="0.1.0")
audit=[]; lab={}
BASE=Path(__file__).resolve().parent

@app.get("/")
def dashboard():
    return FileResponse(BASE/"static"/"index.html")

@app.get("/health")
def health(): return {"status":"ok","service":"codestra-device-forge","host":"appolon"}

@app.get("/api/v1/integrations")
def get_integrations(): return integrations()

@app.get("/api/v1/devices")
def devices(): return discover_android()+discover_apple()

@app.get("/api/v1/restrictions/{device_id}")
def restrictions(device_id:str):
    return {"device_id":device_id,"status":"UNKNOWN","action":"AUTHORIZED_DIAGNOSTICS_REQUIRED","bypass_allowed":False}

@app.get("/api/v1/esim/{device_id}")
def esim(device_id:str):
    return {"device_id":device_id,"capability":"requires-device-probe","provisioning":"authorized-profiles-only"}

@app.get("/api/v1/management/{device_id}")
def management(device_id:str):
    return {"device_id":device_id,"provider":"adapter-required","status":"unknown"}

@app.post("/api/v1/lab/targets")
def create_target(target:LabTarget):
    if not target.synthetic: raise HTTPException(400,"Research targets must be synthetic")
    lab[target.id]=target.model_dump(); audit.append({"event":"lab.target.created","target":target.id})
    return lab[target.id]

@app.post("/api/v1/lab/experiments/{target_id}")
def experiment(target_id:str):
    if target_id not in lab: raise HTTPException(404,"target not found")
    audit.append({"event":"lab.experiment","target":target_id})
    return {"target":target_id,"scope":"synthetic-only","result":"baseline-enforcement-active"}

@app.get("/api/v1/audit")
def get_audit(): return audit
