from __future__ import annotations
import shutil, subprocess
from .models import Integration

TOOLS={
 "adb":("android-transport","adb"),
 "fastboot":("android-transport","fastboot"),
 "ideviceinfo":("apple-transport","ideviceinfo"),
 "heimdall":("samsung-firmware","heimdall"),
}
def integrations():
    return [Integration(id=k,kind=v[0],installed=bool(shutil.which(v[1])),available=bool(shutil.which(v[1])),detail=v[1]) for k,v in TOOLS.items()]

def run_readonly(tool:str,args:list[str],timeout:int=8):
    path=shutil.which(tool)
    if not path: return {"available":False,"output":""}
    p=subprocess.run([path,*args],capture_output=True,text=True,timeout=timeout,check=False)
    return {"available":True,"returncode":p.returncode,"output":(p.stdout+p.stderr)[:12000]}

def discover_android():
    r=run_readonly("adb",["devices","-l"])
    if not r["available"]: return []
    rows=[]
    for line in r["output"].splitlines()[1:]:
        if "\tdevice" in line:
            serial=line.split()[0]
            rows.append({"id":f"android-{serial[-6:]}","platform":"android","serial_masked":"***"+serial[-4:],"connection_mode":"adb"})
    return rows

def discover_apple():
    r=run_readonly("idevice_id",["-l"])
    if not r["available"] or r.get("returncode") != 0: return []
    rows=[]
    for raw in r["output"].splitlines():
        x=raw.strip()
        if not x or "error" in x.lower() or "unable" in x.lower() or "device list" in x.lower(): continue
        if len(x) < 16 or any(c.isspace() for c in x): continue
        rows.append({"id":f"apple-{x[-6:]}","platform":"ios","serial_masked":"***"+x[-4:],"connection_mode":"usbmux"})
    return rows

