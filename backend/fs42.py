import os
import json
import shutil
import random
from pathlib import Path

# === Base paths (auto-detected) ===
ROOT = Path(__file__).resolve().parents[1] / "FieldStation42"
CATALOG_DIR = ROOT / "catalog"
CONF_DIR = ROOT / "confs"

CATALOG_DIR.mkdir(parents=True, exist_ok=True)
CONF_DIR.mkdir(parents=True, exist_ok=True)


# ==== Helpers ====
def generate_conf(ch: dict):
    name = ch["name"]                # Display name (can be mixed case)
    safe_name = name.lower()         # Always lowercase for filesystem
    path = os.path.join(str(CATALOG_DIR), safe_name)

    conf = {
        "station_conf": {
            "network_name": name,  # keep original case for display
            "channel_number": ch["config"].get("channel_number", 1),
            "network_type": ch["config"].get("network_type", "standard"),
            "tags": ch["config"].get("tags", []),
            "tag_colors": ch["config"].get("tag_colors", {}),
        }
    }

    nt = conf["station_conf"]["network_type"]

    if nt == "standard":
        conf["station_conf"].update({
            "content_dir": path,
            "commercial_dir": os.path.join(path, "commercials"),
            "bump_dir": os.path.join(path, "bump"),
            "schedule_increment": ch["config"].get("schedule_increment", 30),
            "break_strategy": ch["config"].get("break_strategy", "standard"),
            "commercial_free": ch["config"].get("commercial_free", False),
            "off_air_path": ch["config"].get("off_air_path", ""),
            "signoff_path": ch["config"].get("signoff_path", "")
        })

        os.makedirs(os.path.join(path, "commercials"), exist_ok=True)
        os.makedirs(os.path.join(path, "bump"), exist_ok=True)

        # === Sync tag folders ===
        active_tags = set(conf["station_conf"]["tags"])
        existing_folders = set()
        if os.path.exists(path):
            for entry in os.scandir(path):
                if entry.is_dir() and entry.name not in ["commercials", "bump"]:
                    existing_folders.add(entry.name)

        # Create any new tag folders
        for tag in active_tags:
            os.makedirs(os.path.join(path, tag), exist_ok=True)

        # Remove stale tag folders if empty
        for folder in existing_folders - active_tags:
            folder_path = os.path.join(path, folder)
            try:
                if not os.listdir(folder_path):  # empty
                    shutil.rmtree(folder_path)
                    print(f"[cleanup] Removed empty tag folder {folder_path}")
            except Exception as e:
                print(f"[cleanup] Could not remove {folder_path}: {e}")

        # === Seed random weekly schedule ===
        available_tags = conf["station_conf"]["tags"]
        days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
        for day in days:
            conf["station_conf"][day] = {}
            for hour in range(24):
                if available_tags:
                    chosen = random.choice(available_tags)
                    conf["station_conf"][day][str(hour)] = {"tags": [chosen]}
                else:
                    conf["station_conf"][day][str(hour)] = {}  # off_air

    elif nt == "loop":
        conf["station_conf"].update({
            "content_dir": path,
            "network_long_name": ch["config"].get("network_long_name", f"{name} Loop"),
            "loop_shuffle": ch["config"].get("loop_shuffle", True),
        })
        os.makedirs(path, exist_ok=True)

    elif nt == "streaming":
        conf["station_conf"].update({
            "runtime_dir": ch["config"].get("runtime_dir", f"runtime/{safe_name}"),
            "network_long_name": ch["config"].get("network_long_name", f"{name} Streaming"),
            "streams": ch["config"].get("streams", []),
        })

    elif nt == "web":
        conf["station_conf"].update({
            "web_url": ch["config"].get("web_url", "")
        })

    # ✅ Save config file with lowercase filename
    conf_path = os.path.join(CONF_DIR, f"{safe_name}.json")
    with open(conf_path, "w") as f:
        json.dump(conf, f, indent=2)


def load_all_channels():
    result = {}
    if not os.path.exists(CONF_DIR):
        return result
    for fn in os.listdir(CONF_DIR):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(CONF_DIR, fn)
        try:
            with open(path) as f:
                data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load {fn}: {e}")
            continue
        if "station_conf" not in data:
            print(f"[WARN] Skipping {fn}, missing station_conf")
            continue
        name = data["station_conf"]["network_name"]
        safe_name = name.lower()
        result[name] = {
            "name": name,
            "path": data["station_conf"].get("content_dir", str(CATALOG_DIR / safe_name)),
            "config": data["station_conf"],
        }
    return result


def delete_channel(name: str):
    safe_name = name.lower()
    conf_path = os.path.join(CONF_DIR, f"{safe_name}.json")
    if os.path.exists(conf_path):
        os.remove(conf_path)
    cat_path = os.path.join(CATALOG_DIR, safe_name)
    if os.path.exists(cat_path):
        shutil.rmtree(cat_path)


def get_schedule(name: str):
    # tolerate mixed case lookups
    all_files = {fn.lower(): fn for fn in os.listdir(CONF_DIR) if fn.endswith(".json")}
    key = f"{name.lower()}.json"
    if key not in all_files:
        raise FileNotFoundError(f"No conf found for {name}")

    conf_path = os.path.join(CONF_DIR, all_files[key])
    with open(conf_path) as f:
        conf = json.load(f)

    schedule = {}
    for day in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]:
        schedule[day] = {}
        for hour, slot in conf["station_conf"].get(day, {}).items():
            tags = slot.get("tags", [])
            if isinstance(tags, str):  # normalize to list
                tags = [tags]
            schedule[day][hour] = {**slot, "tags": tags}
    return schedule


def replace_schedule(name: str, new_schedule: dict):
    safe_name = name.lower()
    conf_path = os.path.join(CONF_DIR, f"{safe_name}.json")
    with open(conf_path) as f:
        conf = json.load(f)

    conf["station_conf"].update(new_schedule)

    # normalize tags everywhere
    for day in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]:
        for hour, slot in conf["station_conf"].get(day, {}).items():
            tags = slot.get("tags", [])
            if isinstance(tags, str):
                conf["station_conf"][day][hour]["tags"] = [tags]

    with open(conf_path, "w") as f:
        json.dump(conf, f, indent=2)
    return conf


def patch_slot(name: str, day: str, hour: int, slot: dict):
    safe_name = name.lower()
    conf_path = os.path.join(CONF_DIR, f"{safe_name}.json")
    with open(conf_path) as f:
        conf = json.load(f)

    if day not in conf["station_conf"]:
        conf["station_conf"][day] = {}

    tags = slot.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]

    conf["station_conf"][day][str(hour)] = {**slot, "tags": tags}

    with open(conf_path, "w") as f:
        json.dump(conf, f, indent=2)
    return conf


def reset_system():
    shutil.rmtree(CATALOG_DIR, ignore_errors=True)
    shutil.rmtree(CONF_DIR, ignore_errors=True)
    os.makedirs(CATALOG_DIR, exist_ok=True)
    os.makedirs(CONF_DIR, exist_ok=True)
