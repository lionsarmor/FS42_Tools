import os
import json
import subprocess
import requests
import time
import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fs42
import uvicorn

app = FastAPI()

# === Paths ===
BASE_DIR = Path(__file__).resolve().parents[1]
CONF_DIR = BASE_DIR / "FieldStation42" / "confs"
RUNTIME_DIR = BASE_DIR / "FieldStation42" / "runtime"
FS42_BIN = Path("/mnt/media01/projects/FS42-Tsar-Tools/fs42-custom/bin")
FS42_FIELDSTATION = Path("/mnt/media01/projects/FS42-Tsar-Tools/FieldStation42")
PYTHON_ENV = "/mnt/media01/projects/FS42-Tsar-Tools/FieldStation42/env/bin/python"
CHANNEL_SOCKET = FS42_FIELDSTATION / "runtime" / "channel.socket"
STATUS_SOCKET = FS42_FIELDSTATION / "runtime" / "play_status.socket"

# === FS42 player API ===
FS42_API = "http://127.0.0.1:4242"

# === Enable CORS for frontend ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # allow all origins
    allow_credentials=True,    # keep cookies/auth if you need them
    allow_methods=["*"],       # allow all HTTP verbs
    allow_headers=["*"],       # allow all headers
)


# === Startup ===
@app.on_event("startup")
def load_existing_channels():
    channels = fs42.load_all_channels()
    print(f"[startup] Loaded {len(channels)} channels from confs/")

# === Helpers ===
def _resolve_channel_name(name: str, channels: dict) -> str:
    lookup = {k.lower(): k for k in channels}
    lname = name.lower()
    if lname not in lookup:
        raise HTTPException(status_code=404, detail="Channel not found")
    return lookup[lname]

def _enforce_baseline(conf: dict) -> dict:
    baseline = fs42._baseline_for_type(conf.get("network_type"))
    baseline.update(conf or {})
    return baseline

def proxy_fs42(path: str, method="GET", data=None):
    try:
        r = requests.request(method, f"{FS42_API}{path}", json=data, timeout=2)
        ct = r.headers.get("content-type", "")
        if ct.startswith("application/json"):
            return r.json()
        return {"status": "ok", "raw": r.text.strip()}
    except Exception as e:
        raise HTTPException(500, f"FS42 request failed: {e}")

# === Save helpers ===
def save_standard_channel(conf: dict, old_name=None):
    """
    Standard/guide/loop channels → enforce baseline, generate schedule,
    create tag folders, etc.
    """
    conf = _enforce_baseline(conf)

    # If no schedule exists but tags are present → generate schedule
    if conf.get("network_type", "standard") == "standard":
        has_schedule = any(
            conf.get(day) for day in
            ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
        )
        if not has_schedule and conf.get("tags"):
            new_schedule = fs42._generate_default_schedule(
                conf.get("tags", []),
                conf.get("schedule_increment", 30)
            )
            conf.update(new_schedule)

    ch = {"name": conf["network_name"], "config": conf}
    fs42.generate_conf(ch, old_name=old_name)
    return {"status": "ok"}

def save_guide_channel(conf: dict, old_name=None):
    """
    Guide channels are a special case: enforce GUIDE_BASELINE_CONF and
    store cleanly under station_conf (no nested station_conf).
    """
    gc = dict(fs42.GUIDE_BASELINE_CONF)
    gc.update(conf or {})

    ch = {"name": gc["network_name"], "config": gc}
    fs42.generate_conf(ch, old_name=old_name)
    return {"status": "ok"}


def save_weather_channel(conf: dict, old_name=None):
    """
    Weather/web/streaming → pass-through. Only web_url matters.
    """
    wc = {
        "network_name": conf.get("network_name", "WeatherTV"),
        "channel_number": conf.get("channel_number", 1),
        "network_type": "web",
        "web_url": conf.get("web_url", ""),
    }
    ch = {"name": wc["network_name"], "config": wc}
    fs42.generate_conf(ch, old_name=old_name)  # stores clean JSON
    return {"status": "ok"}

# === CHANNELS API ===
@app.get("/channels")
def get_channels():
    channels = fs42.load_all_channels()
    empty_map = get_empty_folders()
    for ch in channels.values():
        ch["config"] = _enforce_baseline(ch.get("config", {}))
        ch["emptyFolders"] = empty_map.get(ch["name"], [])
    return list(channels.values())

@app.post("/channels")
def create_channel(payload: dict):
    conf = payload.get("station_conf", payload)
    ntype = conf.get("network_type", "standard")
    if ntype in ("weather", "web", "streaming"):
        return save_weather_channel(conf)
    elif ntype == "guide":
        return save_guide_channel(conf)
    return save_standard_channel(conf)

@app.put("/channels/{name}")
def update_channel(name: str, payload: dict):
    channels = fs42.load_all_channels()
    real_name = _resolve_channel_name(name, channels)
    conf = payload.get("station_conf", payload)
    ntype = conf.get("network_type", "standard")
    if ntype in ("weather", "web", "streaming"):
        return save_weather_channel(conf, old_name=real_name)
    elif ntype == "guide":
        return save_guide_channel(conf, old_name=real_name)
    return save_standard_channel(conf, old_name=real_name)

@app.delete("/channels/{name}")
def delete_channel(name: str):
    channels = fs42.load_all_channels()
    real_name = _resolve_channel_name(name, channels)
    fs42.delete_channel(real_name)
    return {"status": "ok"}

# === Baseline defaults API ===
@app.get("/channels/baseline/{type}")
def get_baseline(type: str):
    if type == "standard":
        return {"station_conf": fs42.BASELINE_CONF}
    elif type == "guide":
        return {"station_conf": fs42.GUIDE_BASELINE_CONF}
    elif type in ("weather", "web", "streaming"):
        return {"station_conf": fs42.WEATHER_BASELINE_CONF}
    else:
        raise HTTPException(400, f"Unknown baseline type: {type}")

# === Normalize API ===
@app.post("/channels/normalize")
def normalize_channels():
    try:
        channels = fs42.load_all_channels()
        updated = []
        skipped = []

        for name, ch in channels.items():
            conf = ch.get("config", {})
            ntype = conf.get("network_type", "standard")

            # Skip special channel types
            if ntype in ("guide", "weather", "web", "streaming"):
                skipped.append(name)
                continue

            # Get fresh baseline for type
            baseline = fs42._baseline_for_type(ntype)

            # Preserve identity
            baseline["network_name"] = conf.get("network_name", name)
            baseline["channel_number"] = conf.get("channel_number", ch.get("channel_number", 1))

            # Always enforce correct dirs
            baseline["bump_dir"] = "bump"
            baseline["commercial_dir"] = "commercial"

            if ntype == "standard":
                # Preserve tags + increment
                baseline["tags"] = conf.get("tags", [])
                baseline["schedule_increment"] = conf.get("schedule_increment", 30)

                # Check if a schedule exists
                has_schedule = any(
                    conf.get(day)
                    for day in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
                )

                if has_schedule:
                    # Copy existing schedule
                    for day in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]:
                        if conf.get(day):
                            baseline[day] = conf[day]
                elif baseline["tags"]:
                    # No schedule but tags exist → generate default
                    baseline.update(
                        fs42._generate_default_schedule(
                            baseline["tags"],
                            baseline["schedule_increment"]
                        )
                    )

            # Write new config
            fs42.generate_conf({"name": baseline["network_name"], "config": baseline})
            updated.append(name)

        return {"status": "ok", "updated": updated, "skipped": skipped}
    except Exception as e:
        raise HTTPException(500, f"Normalization failed: {e}")

# === PLAYER API ===
def _send_socket_command(command: dict):
    """Write a JSON command directly into channel.socket"""
    try:
        with open(CHANNEL_SOCKET, "w") as fp:
            fp.write(json.dumps(command))
    except Exception as e:
        raise HTTPException(500, f"Failed to write to channel socket: {e}")

@app.get("/player/channels/current")
def get_current_channel():
    """Read current player status from play_status.socket"""
    try:
        with open(STATUS_SOCKET, "r") as f:
            return json.loads(f.read().strip())
    except Exception as e:
        raise HTTPException(500, f"Failed to read status: {e}")

@app.post("/player/channels/up")
def channel_up():
    _send_socket_command({"command": "up", "channel": -1})
    return {"status": "ok"}

@app.post("/player/channels/down")
def channel_down():
    _send_socket_command({"command": "down", "channel": -1})
    return {"status": "ok"}

@app.post("/player/channels/{num}")
def tune_channel(num: int):
    _send_socket_command({"command": "direct", "channel": num})
    return {"status": "ok", "channel": num}

@app.post("/player/channel")
def player_channel(cmd: dict):
    """Generic channel command passthrough"""
    if not isinstance(cmd, dict):
        raise HTTPException(400, "Invalid command format")
    _send_socket_command(cmd)
    return {"status": "ok", "command": cmd}

# === Runtime files API ===
@app.get("/api/runtime-files")
def list_runtime_files():
    result = {"off_air_video": [], "sign_off_video": [], "standby_image": [], "be_right_back_media": []}
    if not RUNTIME_DIR.exists():
        return result
    for f in RUNTIME_DIR.iterdir():
        if f.is_file():
            path = f"runtime/{f.name}"
            if f.suffix.lower() in [".mp4", ".mkv", ".avi", ".mov"]:
                result["off_air_video"].append(path)
                result["sign_off_video"].append(path)
                result["be_right_back_media"].append(path)
            if f.suffix.lower() in [".png", ".jpg", ".jpeg", ".gif", ".bmp"]:
                result["standby_image"].append(path)
                result["be_right_back_media"].append(path)
    return result

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
                for folder in base_path.iterdir():
                    if folder.is_dir() and not any(folder.iterdir()):
                        empty.append(folder.name)
        results[name] = empty
    return results

# === Hot Start / Kill / Scanner ===
@app.post("/scanner")
def launch_scanner():
    try:
        cmd = [PYTHON_ENV, str(FS42_FIELDSTATION / "station_42.py")]
        log_path = FS42_FIELDSTATION / "scanner.log"
        env = os.environ.copy()
        env.update({
            "DISPLAY": ":99",
            "HOME": str(Path.home()),
            "PATH": f"{FS42_FIELDSTATION}/env/bin:" + env["PATH"],
            "VIRTUAL_ENV": f"{FS42_FIELDSTATION}/env",
        })

        with open(log_path, "a") as log_file:
            log_file.write("\n=== SCANNER START ===\n")
            log_file.write(f"Timestamp: {datetime.datetime.now()}\n")
            proc = subprocess.Popen(
                cmd, cwd=FS42_FIELDSTATION,
                stdout=log_file, stderr=subprocess.STDOUT, env=env
            )

        return {
            "status": "ok",
            "url": "https://remote.radroddy.com",
            "pid": proc.pid
        }
    except Exception as e:
        raise HTTPException(500, f"Scanner failed: {e}")


@app.post("/hot-start")
def hot_start():
    try:
        subprocess.run(
            ["sudo", "systemctl", "restart", "fs42-hotstart"],
            check=True,
            capture_output=True,
            text=True
        )
        pid_out = subprocess.check_output(
            ["systemctl", "show", "-p", "MainPID", "--value", "fs42-hotstart"]
        ).decode().strip()
        return {
            "status": "ok",
            "pid": int(pid_out) if pid_out.isdigit() else None
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            500,
            f"Hot start failed: {e.stderr or e.stdout or str(e)}"
        )



@app.post("/kill")
def kill_all():
    try:
        script = FS42_BIN / "kill.sh"
        if not script.exists():
            raise FileNotFoundError(f"{script} not found")
        proc = subprocess.Popen(
            ["bash", str(script)], cwd=FS42_BIN,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = proc.communicate(timeout=5)
        return {
            "status": "ok" if proc.returncode == 0 else "error",
            "stdout": out.decode().strip(),
            "stderr": err.decode().strip(),
            "returncode": proc.returncode
        }
    except Exception as e:
        raise HTTPException(500, f"Kill failed: {e}")

@app.get("/fonts")
def list_system_fonts():
    font_dirs = [
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        str(Path.home() / ".fonts"),
        str(Path.home() / ".local/share/fonts"),
    ]
    exts = (".ttf", ".otf", ".ttc")

    found = []
    for d in font_dirs:
        p = Path(d)
        if not p.exists():
            continue
        for f in p.rglob("*"):
            if f.suffix.lower() in exts:
                found.append(f.stem)  # filename without extension

    # Deduplicate + sort
    fonts = sorted(set(found))
    if not fonts:
        fonts = ["Arial", "Courier", "Times New Roman", "Verdana", "Tahoma", "Georgia"]

    return {"fonts": fonts}

 # === Schedule API ===
import random

def _random_color():
    # bright-ish random hex
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

@app.get("/channels/{name}/schedule")
def get_channel_schedule(name: str):
    try:
        schedule = fs42.get_schedule(name)
        confs = fs42.load_all_channels()
        ch = confs.get(name)
        tags = ch["config"].get("tags", []) if ch else []
        tag_colors = dict(ch["config"].get("tag_colors", {}))

        # assign random colors to any missing tags
        for tag in tags:
            if tag not in tag_colors:
                tag_colors[tag] = _random_color()

        return {"schedule": schedule, "tags": tags, "tag_colors": tag_colors}
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch schedule: {e}")

@app.patch("/channels/{name}/schedule/{day}/{hour}")
def patch_channel_slot(name: str, day: str, hour: int, slot: dict):
    try:
        updated_conf = fs42.patch_slot(name, day, hour, slot)
        return {"status": "ok", "schedule": updated_conf.get(day, {})}
    except Exception as e:
        raise HTTPException(500, f"Failed to patch slot: {e}")
   



if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=4343, reload=True)
