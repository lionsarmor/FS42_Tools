from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import subprocess
import os
import requests
import fs42

app = FastAPI()

# === Paths ===
BASE_DIR = Path(__file__).resolve().parents[1]
CONF_DIR = BASE_DIR / "FieldStation42" / "confs"
RUNTIME_DIR = BASE_DIR / "FieldStation42" / "runtime"

# === Enable CORS for frontend ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://100.93.192.114:5173",   # LAN frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def load_existing_channels():
    channels = fs42.load_all_channels()
    print(f"[startup] Loaded {len(channels)} channels from confs/")

# === Helper: normalize channel name ===
def _resolve_channel_name(name: str, channels: dict) -> str:
    lookup = {k.lower(): k for k in channels}
    lname = name.lower()
    if lname not in lookup:
        raise HTTPException(status_code=404, detail="Channel not found")
    return lookup[lname]

# === Helper: enforce baseline keys (important!!) ===
def _enforce_baseline(conf: dict) -> dict:
    """Ensure all baseline keys from fs42.BASELINE_CONF are present."""
    sc = dict(fs42.BASELINE_CONF)
    sc.update(conf or {})
    return sc

# === CHANNELS API ===
@app.get("/channels")
def get_channels():
    channels = fs42.load_all_channels()
    # Inject baseline keys into every config
    for ch in channels.values():
        ch["config"] = _enforce_baseline(ch.get("config", {}))
    return list(channels.values())

@app.post("/channels")
def create_channel(payload: dict):
    """Create a new channel"""
    conf = payload.get("station_conf", payload)
    conf = _enforce_baseline(conf)
    ch = {
        "name": conf.get("network_name", "UnnamedChannel"),
        "config": conf
    }
    fs42.generate_conf(ch)
    return {"status": "ok"}

@app.put("/channels/{name}")
def update_channel(name: str, payload: dict):
    """Update existing channel"""
    channels = fs42.load_all_channels()
    real_name = _resolve_channel_name(name, channels)

    conf = payload.get("station_conf", payload)
    conf = _enforce_baseline(conf)
    ch = {
        "name": conf.get("network_name", real_name),
        "config": conf
    }
    fs42.generate_conf(ch)
    return {"status": "ok"}

@app.delete("/channels/{name}")
def delete_channel(name: str):
    channels = fs42.load_all_channels()
    real_name = _resolve_channel_name(name, channels)
    fs42.delete_channel(real_name)
    return {"status": "ok"}

# === SCHEDULE API ===
@app.get("/channels/{name}/schedule")
def get_schedule(name: str):
    try:
        schedule = fs42.get_schedule(name)
        channels = fs42.load_all_channels()
        real_name = _resolve_channel_name(name, channels)
        conf = _enforce_baseline(channels[real_name]["config"])
        return {
            "schedule": schedule,
            "tags": conf.get("tags", []),
            "tag_colors": conf.get("tag_colors", {})
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get schedule: {e}")

@app.put("/channels/{name}/schedule")
def replace_schedule(name: str, schedule: dict):
    try:
        updated = fs42.replace_schedule(name, schedule)
        updated["station_conf"] = _enforce_baseline(updated["station_conf"])
        return {"status": "ok", "conf": updated}
    except Exception as e:
        raise HTTPException(500, f"Failed to replace schedule: {e}")

@app.patch("/channels/{name}/schedule/{day}/{hour}")
def patch_schedule_slot(name: str, day: str, hour: int, slot: dict):
    try:
        updated = fs42.patch_slot(name, day, hour, slot)
        updated["station_conf"] = _enforce_baseline(updated["station_conf"])
        return {"status": "ok", "conf": updated}
    except Exception as e:
        raise HTTPException(500, f"Failed to patch slot: {e}")

# === Bumps API ===
@app.get("/channels/{name}/bump")
def get_bump_files(name: str):
    channels = fs42.load_all_channels()
    real_name = _resolve_channel_name(name, channels)
    conf = _enforce_baseline(channels[real_name]["config"])
    bump_dir = conf.get("bump_dir", "bump")
    bump_path = BASE_DIR / "FieldStation42" / bump_dir
    if not bump_path.exists():
        return []
    return [f.name for f in bump_path.iterdir() if f.is_file()]

# === PLAYER API (proxy to FS42 on 4242) ===
FS42_API = "http://127.0.0.1:4242"

def proxy_fs42(path: str):
    """Forward GET request to FS42 API and always return JSON-safe."""
    try:
        r = requests.get(f"{FS42_API}{path}", timeout=2)
        ct = r.headers.get("content-type", "")
        if ct.startswith("application/json"):
            return r.json()
        return {"status": "ok", "raw": r.text.strip()}
    except Exception as e:
        raise HTTPException(500, f"FS42 request failed: {e}")

@app.get("/player/channels/current")
def get_current_channel():
    return proxy_fs42("/player/channels/current")

@app.get("/player/channels/up")
def channel_up():
    return proxy_fs42("/player/channels/up")

@app.get("/player/channels/down")
def channel_down():
    return proxy_fs42("/player/channels/down")

@app.get("/player/channels/{num}")
def tune_channel(num: int):
    return proxy_fs42(f"/player/channels/{num}")

@app.get("/player/health")
def player_health():
    try:
        r = requests.get("http://127.0.0.1:8889/mystream/", timeout=2)
        return {"live": r.status_code == 200}
    except:
        return {"live": False}

# === Hot Start endpoint ===
@app.post("/hot-start")
def hot_start():
    try:
        BIN_DIR = BASE_DIR / "fs42-custom" / "bin"
        SCRIPT = BIN_DIR / "start.sh"
        LOGFILE = BIN_DIR / "hotstart.log"

        subprocess.Popen(
            ["bash", str(SCRIPT)],
            cwd=str(BIN_DIR),
            stdout=open(LOGFILE, "a"),
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True
        )
        return {"status": "ok", "message": "Hot Start launched"}
    except Exception as e:
        return {"error": str(e)}

# === Kill endpoint ===
@app.post("/kill")
def kill_all():
    try:
        BIN_DIR = BASE_DIR / "fs42-custom" / "bin"
        SCRIPT = BIN_DIR / "kill.sh"
        LOGFILE = BIN_DIR / "kill.log"

        subprocess.Popen(
            ["bash", str(SCRIPT)],
            cwd=str(BIN_DIR),
            stdout=open(LOGFILE, "a"),
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True
        )
        return {"status": "ok", "message": "Kill script launched"}
    except Exception as e:
        return {"error": str(e)}

# === Empty folders check ===
@app.get("/channels-empty-folders")
def get_empty_folders():
    channels = fs42.load_all_channels()
    results = {}

    for name, ch in channels.items():
        conf = _enforce_baseline(ch.get("config", {}))
        content_dir = conf.get("content_dir")
        empty = []

        if content_dir:
            base_path = Path(content_dir)
            if not base_path.is_absolute():
                base_path = Path(fs42.CATALOG_DIR) / Path(content_dir).name

            if base_path.exists():
                # check only immediate subfolders
                for folder in base_path.iterdir():
                    if folder.is_dir() and not any(folder.iterdir()):
                        empty.append(folder.name)

        results[name] = empty

    return results

# === Fonts API ===
@app.get("/fonts")
def list_fonts():
    """Return a list of system fonts (requires fontconfig)."""
    try:
        result = subprocess.run(
            ["fc-list", ":", "family"],
            capture_output=True, text=True, check=True
        )
        fonts = sorted(set(line.strip().split(",")[0] for line in result.stdout.splitlines() if line.strip()))
        return {"fonts": fonts}
    except Exception as e:
        raise HTTPException(500, f"Failed to list fonts: {e}")

# === Runtime files API ===
@app.get("/api/runtime-files")
def list_runtime_files():
    result = {
        "off_air_video": [],
        "sign_off_video": [],
        "standby_image": [],
        "be_right_back_media": [],
    }

    if not RUNTIME_DIR.exists():
        return result

    for f in RUNTIME_DIR.iterdir():
        if f.is_file():
            # Videos
            if f.suffix.lower() in [".mp4", ".mkv", ".avi", ".mov"]:
                result["off_air_video"].append(f.name)
                result["sign_off_video"].append(f.name)
                result["be_right_back_media"].append(f.name)
            # Images
            if f.suffix.lower() in [".png", ".jpg", ".jpeg", ".gif", ".bmp"]:
                result["standby_image"].append(f.name)
                result["be_right_back_media"].append(f.name)

    return result


@app.post("/channels/normalize")
def normalize_channels():
    """Normalize all channel configs to the latest schema."""
    try:
        channels = fs42.load_all_channels()
        updated = []
        for name, ch in channels.items():
            fs42.generate_conf(ch)  # will rewrite with enforced keys
            updated.append(name)
        return {"status": "ok", "updated": updated}
    except Exception as e:
        raise HTTPException(500, f"Normalization failed: {e}")
