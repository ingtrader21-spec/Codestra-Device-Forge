from pathlib import Path
import json, os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .adapters import integrations, discover_android, discover_apple
from .models import LabTarget
from .storage import init_db, upsert_device, get_device, list_devices, create_job, get_job, list_jobs, set_job_state, list_audit, audit
from .providers import provider_health, device_actions, openeuicc_status

app=FastAPI(title="Codestra Device Forge",version="0.2.0")
BASE=Path(__file__).resolve().parent
CATALOG=BASE.parent/"catalog"
init_db()
lab={}

class JobRequest(BaseModel):
    kind:str
    device_id:str|None=None
    payload:dict={}
    requires_approval:bool=True

@app.get("/",include_in_schema=False)
def dashboard(): return FileResponse(BASE/"static"/"index.html")

@app.get("/health")
def health(): return {"status":"ok","service":"codestra-device-forge","host":os.uname().nodename if hasattr(os,"uname") else "device-forge","version":"0.2.0"}

@app.get("/api/v1/integrations")
def get_integrations(): return integrations()

@app.get("/api/v1/providers")
def get_providers(): return provider_health()

@app.get("/api/v1/providers/{provider_id}/health")
def provider(provider_id:str):
    p=next((x for x in provider_health() if x["id"]==provider_id),None)
    if not p: raise HTTPException(404,"provider not found")
    return p

@app.get("/api/v1/esim/providers/openeuicc")
def get_openeuicc(): return openeuicc_status()

@app.get("/api/v1/esim/providers/openeuicc/{device_id}")
def get_openeuicc_device(device_id:str): return openeuicc_status(device_id)

@app.get("/api/v1/devices")
def devices():
    found=discover_android()+discover_apple()
    for d in found: upsert_device(d)
    return found

@app.get("/api/v1/devices/registry")
def registry(): return list_devices()

@app.get("/api/v1/devices/{device_id}")
def detail(device_id:str):
    d=get_device(device_id)
    if not d: raise HTTPException(404,"device not found in registry")
    d["snapshot"]=json.loads(d["snapshot_json"])
    return d

@app.get("/api/v1/devices/{device_id}/actions")
def actions(device_id:str):
    d=get_device(device_id)
    if not d:
        live=next((x for x in devices() if x["id"]==device_id),None)
        if not live: raise HTTPException(404,"device not found")
        d=live
    return {"device_id":device_id,"actions":device_actions(d)}

@app.post("/api/v1/devices/{device_id}/probe")
def probe(device_id:str):
    live=next((x for x in devices() if x["id"]==device_id),None)
    if not live: raise HTTPException(404,"device not currently connected")
    audit("device.probed",device_id,live)
    return {"device":live,"actions":device_actions(live)}

@app.get("/api/v1/restrictions/{device_id}")
def restrictions(device_id:str): return {"device_id":device_id,"status":"UNKNOWN","action":"AUTHORIZED_DIAGNOSTICS_REQUIRED","bypass_allowed":False}

@app.get("/api/v1/esim/{device_id}")
def esim(device_id:str): return {"device_id":device_id,"provider":"openeuicc","provider_status":openeuicc_status(device_id),"provisioning":"authorized-profiles-only"}

@app.get("/api/v1/management/{device_id}")
def management(device_id:str): return {"device_id":device_id,"provider":"mdmesh","status":"adapter-readback-pending"}

@app.get("/api/v1/catalog/os")
def os_catalog(): return json.loads((CATALOG/"os-catalog.json").read_text())

@app.get("/api/v1/catalog/apps")
def app_catalog(): return json.loads((CATALOG/"post-install-apps.json").read_text())

@app.post("/api/v1/jobs")
def new_job(req:JobRequest):
    if req.device_id and not get_device(req.device_id): raise HTTPException(404,"device not found in registry")
    return create_job(req.kind,req.device_id,req.payload,req.requires_approval)

@app.get("/api/v1/jobs")
def jobs(): return list_jobs()

@app.get("/api/v1/jobs/{job_id}")
def job(job_id:str):
    j=get_job(job_id)
    if not j: raise HTTPException(404,"job not found")
    return j

@app.post("/api/v1/jobs/{job_id}/approve")
def approve(job_id:str):
    j=get_job(job_id)
    if not j: raise HTTPException(404,"job not found")
    if j["state"]!="AWAITING_APPROVAL": raise HTTPException(409,f"job is {j['state']}")
    return set_job_state(job_id,"READY",{"approval":"recorded"})

@app.post("/api/v1/jobs/{job_id}/cancel")
def cancel(job_id:str):
    j=get_job(job_id)
    if not j: raise HTTPException(404,"job not found")
    if j["state"] in {"COMPLETE","CANCELLED"}: raise HTTPException(409,f"job is {j['state']}")
    return set_job_state(job_id,"CANCELLED")

@app.post("/api/v1/lab/targets")
def create_target(target:LabTarget):
    if not target.synthetic: raise HTTPException(400,"Research targets must be synthetic")
    lab[target.id]=target.model_dump(); audit("lab.target.created",target.id,lab[target.id]); return lab[target.id]

@app.post("/api/v1/lab/experiments/{target_id}")
def experiment(target_id:str):
    if target_id not in lab: raise HTTPException(404,"target not found")
    audit("lab.experiment",target_id,{"scope":"synthetic-only"})
    return {"target":target_id,"scope":"synthetic-only","result":"baseline-enforcement-active"}

@app.get("/api/v1/audit")
def get_audit(): return list_audit()

app.mount("/static",StaticFiles(directory=BASE/"static"),name="static")
