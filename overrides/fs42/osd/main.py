#!/usr/bin/env python3
# FS42 → MPV OSD (single-file, loud logs, no extras)

import json, socket, time
from pathlib import Path

# --- config ---
MPV_SOCKET = "/tmp/mpvsocket"
SOURCES = [
    Path("/mnt/media01/projects/FS42-Tsar-Tools/FieldStation42/runtime/play_status.socket"),
    Path("/mnt/media01/projects/FS42-Tsar-Tools/FieldStation42/runtime/channel.socket"),
]
OSD_DURATION_MS = 3000
OSD_LEVEL = 1
POLL_SEC = 0.1
# --------------

def _send_show(text: str):
    if not text:
        return
    payload = {"command": ["show-text", text, OSD_DURATION_MS, OSD_LEVEL]}
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(1.5)
            s.connect(MPV_SOCKET)
            s.send((json.dumps(payload) + "\n").encode("utf-8"))
        print(f"[MPV] show-text OK: {text}")
    except Exception as e:
        print(f"[MPV] IPC error: {e}")

def _safe_json(raw: str):
    raw = (raw or "").strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        # try last non-empty line (some writers append)
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        if not lines:
            return {}
        try:
            return json.loads(lines[-1])
        except Exception:
            return {}

def _flatten(d):
    if isinstance(d, dict):
        for k in ("play_status", "status", "state"):
            v = d.get(k)
            if isinstance(v, dict):
                return v
    return d if isinstance(d, dict) else {}

def _norm_chan(v):
    if v is None:
        return None
    try:
        return str(int(str(v).strip()))
    except Exception:
        return None

def _format_line(d: dict):
    s = _flatten(d)
    chan = _norm_chan(
        s.get("channel_number") or s.get("channel_num") or
        s.get("current_channel") or s.get("channel")
    )
    net = (
        s.get("network_long_name") or s.get("network_name") or
        s.get("network") or s.get("name") or
        s.get("network_display") or s.get("network_long")
    )
    if chan and net: 
        return f"{chan} - {net}"
    if chan:         
        return f"{chan}"
    if net:          
        return f"{net}"
    return ""


def _read_text(p: Path):
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        time.sleep(0.05)  # tiny retry for partial write
        try:
            return p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""

def main():
    print("[OSD] === fs42/osd/main.py start ===")
    print("[OSD] MPV socket:", MPV_SOCKET)
    for p in SOURCES:
        print("[OSD] watching:", p)

    mtimes = {p: 0 for p in SOURCES}
    last_line = ""

    # initial dump
    for p in SOURCES:
        if p.exists():
            st = p.stat()
            print(f"[DBG] {p.name} exists: mtime={int(st.st_mtime)} size={st.st_size}")
        else:
            print(f"[DBG] {p.name} missing")

    while True:
        try:
            fired = False
            for p in SOURCES:
                if not p.exists():
                    continue
                st = p.stat()
                m = int(st.st_mtime)
                if m != mtimes[p]:
                    mtimes[p] = m
                    fired = True
                    raw = _read_text(p)
                    print(f"[DBG] change {p.name}: mtime={m} size={st.st_size} raw[:200]={raw[:200]!r}")
                    data = _safe_json(raw)
                    print(f"[DBG] parsed from {p.name}: {data}")
                    line = _format_line(data)
                    if line:
                        if line != last_line:
                            print(f"[OSD] {p.name} → {line}")
                            _send_show(line)
                            last_line = line
                        else:
                            print(f"[OSD] dedup (same line): {line}")
                    else:
                        print(f"[OSD] no usable fields in {p.name}")
            if not fired:
                time.sleep(POLL_SEC)
        except KeyboardInterrupt:
            print("[OSD] stop (Ctrl+C)")
            break
        except Exception as e:
            print(f"[OSD] loop error: {e}")
            time.sleep(POLL_SEC)

if __name__ == "__main__":
    main()
