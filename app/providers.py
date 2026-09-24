from __future__ import annotations
import os, shutil, urllib.request, urllib.error
from .adapters import run_readonly
def _http(url,timeout=3):
    try:
        r=urllib.request.urlopen(url,timeout=timeout); return True,getattr(r,"status",200)
    except urllib.error.HTTPError as e: return (e.code < 500), e.code
    except Exception as e: return False,str(e)
def provider_health():
    out=[]
    for pid,kind,tool in [("adb","transport","adb"),("fastboot","transport","fastboot"),("apple","transport","ideviceinfo"),("heimdall","firmware","heimdall")]:
        ok=bool(shutil.which(tool)); out.append({"id":pid,"kind":kind,"available":ok,"mode":"host-tool","detail":tool})
    md=os.getenv("MDMESH_URL","http://127.0.0.1:18080"); ok,detail=_http(md); out.append({"id":"mdmesh","kind":"management","available":ok,"mode":"http","detail":str(detail),"endpoint":md})
    mobsf=os.getenv("MOBSF_URL","http://mobsf:8000"); ok,detail=_http(mobsf); out.append({"id":"mobsf","kind":"security","available":ok,"mode":"http","detail":str(detail),"endpoint":mobsf})
    out.append({"id":"openeuicc","kind":"esim","available":bool(shutil.which("adb")),"mode":"android-app","detail":"Requires a compatible Android device and OpenEUICC/EasyEUICC installation"})
    return out
def openeuicc_status(device_id=None):
    base={"provider":"openeuicc","host_adb_available":bool(shutil.which("adb")),"device_id":device_id,"status":"DEVICE_REQUIRED","privileged":None,"capabilities":["detect_euicc","list_profiles","authorized_profile_provisioning","profile_enable_disable"]}
    if not device_id: return base
    r=run_readonly("adb",["-s",device_id,"shell","pm","list","packages"])
    if not r.get("available") or r.get("returncode")!=0: base["status"]="DEVICE_UNAVAILABLE"; return base
    txt=r.get("output","").lower(); hits=[x for x in txt.splitlines() if "euicc" in x or "openeuicc" in x]
    base["packages"]=hits; base["status"]="APP_DETECTED" if hits else "APP_NOT_DETECTED"; return base
def device_actions(device):
    did=device["id"]
    return {
      "probe":{"enabled":True,"method":"POST","endpoint":f"/api/v1/devices/{did}/probe"},
      "restrictions":{"enabled":True,"method":"GET","endpoint":f"/api/v1/restrictions/{did}"},
      "esim_check":{"enabled":True,"method":"GET","endpoint":f"/api/v1/esim/{did}"},
      "management_check":{"enabled":True,"method":"GET","endpoint":f"/api/v1/management/{did}"},
      "install_os":{"enabled":False,"reason":"Compatibility, verified image, backup and approval plan required"},
      "flash_firmware":{"enabled":False,"reason":"No verified installation plan"},
      "remove_security_lock":{"enabled":False,"reason":"Authorized release workflow required"}
    }
