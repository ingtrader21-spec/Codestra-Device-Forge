from __future__ import annotations
import shutil

PROVIDERS={
    "adb":{"kind":"transport","tool":"adb"},
    "fastboot":{"kind":"transport","tool":"fastboot"},
    "apple":{"kind":"transport","tool":"ideviceinfo"},
    "heimdall":{"kind":"firmware","tool":"heimdall"},
    "mdmesh":{"kind":"management","tool":None},
    "mobsf":{"kind":"security","tool":None},
}

def provider_health():
    out=[]
    for pid,p in PROVIDERS.items():
        if p["tool"]:
            ok=bool(shutil.which(p["tool"])); detail=p["tool"]
        else:
            ok=False; detail="adapter configuration required"
        out.append({"id":pid,"kind":p["kind"],"available":ok,"detail":detail})
    return out

def device_actions(device):
    did=device["id"]
    return {
        "probe":{"enabled":True,"method":"POST","endpoint":f"/api/v1/devices/{did}/probe"},
        "restrictions":{"enabled":True,"method":"GET","endpoint":f"/api/v1/restrictions/{did}"},
        "esim_check":{"enabled":True,"method":"GET","endpoint":f"/api/v1/esim/{did}"},
        "management_check":{"enabled":True,"method":"GET","endpoint":f"/api/v1/management/{did}"},
        "install_os":{"enabled":False,"reason":"Compatibility, verified image, backup and approval plan required"},
        "flash_firmware":{"enabled":False,"reason":"No verified installation plan"},
        "remove_security_lock":{"enabled":False,"reason":"Authorized release workflow required"},
    }
