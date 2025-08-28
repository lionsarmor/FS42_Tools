from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import fs42
import os
import shutil
import subprocess

app = FastAPI()

# === Enable CORS for frontend ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # in prod, restrict to frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Paths ===
BASE_DIR = Path(__file__).resolve().parents[1]
RUNTIME_DIR = BASE_DIR / "FieldStation42" / "runtime"


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


# === CHANNELS API ===
@app.get("/channels")
def get_channels():
    return list(fs42.load_all_channels().values())


@app.post("/channels")
def create_channel(ch: dict):
    fs42.generate_conf(ch)
    return {"status": "ok"}


@app.put("/channels/{name}")
def update_channel(name: str, ch: dict):
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
    channels = fs42.load_all_channels()
    real_name = _resolve_channel_name(name, channels)
    return fs42.get_schedule(real_name)


@app.put("/channels/{name}/schedule")
def replace_schedule(name: str, schedule: dict):
    channels = fs42.load_all_channels()
    real_name = _resolve_channel_name(name, channels)
    return fs42.replace_schedule(real_name, schedule)


@app.patch("/channels/{name}/schedule/{day}/{hour}")
def patch_slot(name: str, day: str, hour: int, slot: dict):
    channels = fs42.load_all_channels()
    real_name = _resolve_channel_name(name, channels)
    return fs42.patch_slot(real_name, day, int(hour), slot)


# === BUMP FILES ===
@app.get("/channels/{name}/bump")
def get_bumps(name: str):
    channels = fs42.load_all_channels()
    real_name = _resolve_channel_name(name, channels)

    bump_dir = os.path.join(str(fs42.CATALOG_DIR), real_name.lower(), "bump")

    if not os.path.isdir(bump_dir):
        return []

    return sorted([
        f for f in os.listdir(bump_dir)
        if os.path.isfile(os.path.join(bump_dir, f))
    ])


# === RUNTIME FILES ===
@app.get("/runtime-files")
def list_runtime_files():
    if not RUNTIME_DIR.exists():
        return {"files": []}

    files = [
        f.name for f in RUNTIME_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in [".mp4", ".mkv", ".avi", ".mov"]
    ]
    return {"files": sorted(files)}


# === EMPTY FOLDERS (bulk) ===
@app.get("/channels-empty-folders")
def get_channels_empty_folders():
    channels = fs42.load_all_channels()
    result = {}
    for name, ch in channels.items():
        empty = []
        content_dir = Path(ch["config"].get("content_dir", ""))
        if content_dir.exists():
            for entry in content_dir.iterdir():
                if entry.is_dir() and not any(entry.iterdir()):
                    empty.append(entry.name)
        result[name] = empty
    return result


# === FILE IMPORT (copy/move) ===
@app.post("/channels/{name}/import-files")
def import_files(name: str, payload: dict):
    """
    payload = {
      "files": ["/path/to/file1.mp4", "/path/to/file2.mkv"],
      "target": "movies",
      "action": "copy" | "move"
    }
    """
    channels = fs42.load_all_channels()
    real_name = _resolve_channel_name(name, channels)
    ch = channels[real_name]
    content_dir = Path(ch["config"].get("content_dir", ""))
    if not content_dir.exists():
        raise HTTPException(400, f"Content dir {content_dir} does not exist")

    target_dir = content_dir / payload.get("target", "")
    target_dir.mkdir(parents=True, exist_ok=True)

    action = payload.get("action", "copy")
    moved = []
    for f in payload.get("files", []):
        src = Path(f)
        if not src.exists():
            continue
        dest = target_dir / src.name
        if action == "move":
            shutil.move(str(src), str(dest))
        else:
            shutil.copy2(str(src), str(dest))
        moved.append(str(dest))

    return {"status": "ok", "files": moved}


# === LAUNCH CATALOG SCANNER ===
@app.post("/launch-scanner")
def launch_scanner():
    subprocess.Popen(
        ["/mnt/media01/projects/FS42-Tsar-Tools/FieldStation42/env/bin/python", "station_42.py"],
        cwd="/mnt/media01/projects/FS42-Tsar-Tools/FieldStation42",
        stdout=open("/mnt/media01/projects/FS42-Tsar-Tools/FieldStation42/scanner.log", "w"),
        stderr=subprocess.STDOUT
    )
    return {"url": "http://127.0.0.1:4242/"}


# === HOT START ===
@app.post("/hot-start")
def hot_start():
    subprocess.Popen(
        ["bash", "-c", "source ../FieldStation42/env/bin/activate && ./start.sh"],
        cwd="/mnt/media01/projects/FS42-Tsar-Tools/fs42-custom/bin",
        stdout=open("/mnt/media01/projects/FS42-Tsar-Tools/fs42-custom/bin/hotstart.log", "w"),
        stderr=subprocess.STDOUT
    )
    return {"status": "ok"}

