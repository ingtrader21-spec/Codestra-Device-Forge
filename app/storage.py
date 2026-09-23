from __future__ import annotations
import json, sqlite3, uuid
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "device_forge.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS devices(
          id TEXT PRIMARY KEY, platform TEXT NOT NULL, manufacturer TEXT,
          model TEXT, serial_masked TEXT, connection_mode TEXT,
          last_seen TEXT NOT NULL, snapshot_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS jobs(
          id TEXT PRIMARY KEY, device_id TEXT, kind TEXT NOT NULL,
          state TEXT NOT NULL, requires_approval INTEGER NOT NULL DEFAULT 1,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
          payload_json TEXT NOT NULL, result_json TEXT
        );
        CREATE TABLE IF NOT EXISTS audit_events(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL,
          event TEXT NOT NULL, subject TEXT, detail_json TEXT NOT NULL
        );
        """)

def now(): return datetime.now(timezone.utc).isoformat()

def audit(event, subject=None, detail=None):
    with _conn() as c:
        c.execute("INSERT INTO audit_events(ts,event,subject,detail_json) VALUES(?,?,?,?)",
                  (now(), event, subject, json.dumps(detail or {})))

def upsert_device(d):
    snap=dict(d)
    with _conn() as c:
        c.execute("""INSERT INTO devices(id,platform,manufacturer,model,serial_masked,connection_mode,last_seen,snapshot_json)
        VALUES(?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET platform=excluded.platform,manufacturer=excluded.manufacturer,
        model=excluded.model,serial_masked=excluded.serial_masked,connection_mode=excluded.connection_mode,
        last_seen=excluded.last_seen,snapshot_json=excluded.snapshot_json""",
        (snap["id"],snap["platform"],snap.get("manufacturer"),snap.get("model"),snap.get("serial_masked"),
         snap.get("connection_mode","unknown"),now(),json.dumps(snap)))
    return snap

def get_device(device_id):
    with _conn() as c:
        r=c.execute("SELECT * FROM devices WHERE id=?",(device_id,)).fetchone()
        return dict(r) if r else None

def list_devices():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM devices ORDER BY last_seen DESC")]

def create_job(kind, device_id=None, payload=None, requires_approval=True):
    jid=str(uuid.uuid4()); ts=now(); state="AWAITING_APPROVAL" if requires_approval else "READY"
    with _conn() as c:
        c.execute("INSERT INTO jobs(id,device_id,kind,state,requires_approval,created_at,updated_at,payload_json) VALUES(?,?,?,?,?,?,?,?)",
                  (jid,device_id,kind,state,1 if requires_approval else 0,ts,ts,json.dumps(payload or {})))
    audit("job.created",jid,{"device_id":device_id,"kind":kind,"state":state})
    return get_job(jid)

def get_job(job_id):
    with _conn() as c:
        r=c.execute("SELECT * FROM jobs WHERE id=?",(job_id,)).fetchone()
        return dict(r) if r else None

def list_jobs():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 100")]

def set_job_state(job_id,state,result=None):
    with _conn() as c:
        c.execute("UPDATE jobs SET state=?,updated_at=?,result_json=? WHERE id=?",
                  (state,now(),json.dumps(result) if result is not None else None,job_id))
    audit("job.state",job_id,{"state":state})
    return get_job(job_id)

def list_audit():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM audit_events ORDER BY id DESC LIMIT 200")]
