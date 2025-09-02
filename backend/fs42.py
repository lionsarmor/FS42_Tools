import os
import json
import shutil
from pathlib import Path

# === Base paths ===
ROOT = Path(__file__).resolve().parents[1] / "FieldStation42"
CATALOG_DIR = ROOT / "catalog"
CONF_DIR = ROOT / "confs"

# Ensure base dirs exist
CATALOG_DIR.mkdir(parents=True, exist_ok=True)
CONF_DIR.mkdir(parents=True, exist_ok=True)


# === Guide baseline config (1080p fullscreen) ===
GUIDE_BASELINE_CONF = {
    "network_name": "Guide",
    "channel_number": 1,
    "network_type": "guide",
    "runtime_dir": "runtime/guide",

    # Sound
    "play_sound": True,
    "sound_to_play": "runtime/guide/background.mp3",

    # Appearance defaults
    "fullscreen": True,
    "width": 1920,
    "height": 1080,
    "window_decorations": False,
    "top_bg": "blue3",
    "bottom_bg": "blue4",
    "pad": 20,

    # Messages/images
    "messages": [
        "FieldStation42\nCable Entertainment",
        "Cheers!\nFrom us to you!",
        "FieldStation42 Guide\nOn cable mode."
    ],
    "message_rotation_rate": 10,
    "message_fg": "white",
    "message_font_family": "Arial",
    "message_font_size": 32,

    "images": [
        "runtime/guide/image0.png",
        "runtime/guide/image1.png",
        "runtime/guide/image2.png"
    ],

    # Fonts for overlays
    "network_font_family": "Arial",
    "network_font_size": 20,
    "schedule_font_family": "Arial",
    "schedule_font_size": 20,
    "schedule_highlight_fg": "yellow",
    "schedule_fg": "white",
    "schedule_border_width": 4,
    "schedule_border_relief": "raised",

    # Footer
    "footer_messages": [
        "You are watching FieldStation42",
        "Now with cable mode."
    ],
    "footer_height": 100,

    # Guide behavior
    "schedule_row_count": 3,
    "normalize_title": True,
}

# === Standard channel baseline ===
BASELINE_CONF = {
    "network_name": "",
    "channel_number": 1,
    "network_type": "standard",

    "content_dir": "",
    "commercial_dir": "commercial",
    "bump_dir": "bump",
    "tags": [],
    "tag_colors": {},

    "schedule_increment": 30,
    "break_strategy": "standard",
    "commercial_free": False,
    "break_duration": 120,

    "off_air_video": "runtime/off_air_pattern.mp4",
    "sign_off_video": "runtime/signoff.mp4",
    "standby_image": "runtime/standby.png",
    "be_right_back_media": "runtime/brb.png",

    "clip_shows": [],
    "special_subfolders": [],

    "video_scramble_fx": "",
    "station_fx": "",
    "panscan": 1.0,
    "video_keepaspect": True,
}


# ==== Helpers ====
def generate_conf(ch: dict):
    """
    Generate a station config file.
    Guide channels use GUIDE_BASELINE_CONF instead of BASELINE_CONF.
    """
    name = ch.get("name") or ch.get("config", {}).get("network_name") or "UnnamedChannel"
    safe_name = name.lower()
    user_conf = ch.get("config", {})

    # Pick baseline based on type
    if user_conf.get("network_type") == "guide":
        sc = dict(GUIDE_BASELINE_CONF)
    else:
        sc = dict(BASELINE_CONF)

    sc.update(user_conf)
    sc["network_name"] = name

    # For standard channels, enforce catalog paths
    if sc.get("network_type") != "guide":
        content_dir = f"catalog/{safe_name}"
        sc["content_dir"] = content_dir

        # Ensure channel dirs exist
        os.makedirs(Path(content_dir), exist_ok=True)
        os.makedirs(Path(CATALOG_DIR) / safe_name / "commercial", exist_ok=True)
        os.makedirs(Path(CATALOG_DIR) / safe_name / "bump", exist_ok=True)
        for tag in sc.get("tags", []):
            os.makedirs(Path(CATALOG_DIR) / safe_name / tag, exist_ok=True)

        # Special subfolders
        for sf in sc.get("special_subfolders", []):
            if isinstance(sf, dict):
                value = sf.get("value", "").strip()
                if value:
                    base = Path(CATALOG_DIR) / safe_name
                    if sf.get("type") == "bump":
                        base = base / "bump"
                    os.makedirs(base / value, exist_ok=True)

        # Default schedule if missing
        if not any(day in sc for day in [
            "monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday"
        ]):
            for day in [
                "monday", "tuesday", "wednesday",
                "thursday", "friday", "saturday", "sunday"
            ]:
                sc[day] = {}
                for h in range(24):
                    sc[day][str(h)] = {"tags": sc["tags"] or []}

    # Save JSON
    conf_path = Path(CONF_DIR) / f"{safe_name}.json"
    with open(conf_path, "w") as f:
        json.dump({"station_conf": sc}, f, indent=2)


def load_all_channels():
    """Load all channel configs and normalize them to baselines"""
    result = {}
    if not os.path.exists(CONF_DIR):
        return result

    for fn in os.listdir(CONF_DIR):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(CONF_DIR, fn)) as f:
                data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load {fn}: {e}")
            continue

        sc = data.get("station_conf")
        if not sc:
            print(f"[WARN] Skipping {fn}, missing station_conf")
            continue

        # Merge against the correct baseline
        if sc.get("network_type") == "guide":
            merged = dict(GUIDE_BASELINE_CONF)
        else:
            merged = dict(BASELINE_CONF)
        merged.update(sc)

        # Always enforce a safe name
        name = merged.get("network_name") or fn.replace(".json", "")
        if not name:
            name = "UnnamedChannel"
        safe_name = name.lower()

        result[name] = {
            "name": name,
            "path": merged.get("content_dir", str(CATALOG_DIR / safe_name)),
            "config": merged
        }

        # Rewrite normalized file
        conf_path = Path(CONF_DIR) / fn
        with open(conf_path, "w") as f:
            json.dump({"station_conf": merged}, f, indent=2)

    return result


def delete_channel(name: str):
    """Delete only the config JSON.
    Never remove a catalog directory if it contains files.
    """
    safe_name = name.lower()

    # Delete config file
    conf_path = Path(CONF_DIR) / f"{safe_name}.json"
    if conf_path.exists():
        conf_path.unlink()

    # Check catalog path
    cat_path = Path(CATALOG_DIR) / safe_name
    if cat_path.exists():
        if not any(cat_path.iterdir()):  # Only delete if empty
            shutil.rmtree(cat_path)
        else:
            print(f"[SAFEGUARD] Not deleting {cat_path}, directory not empty.")


def get_schedule(name: str):
    """Return weekly schedule (normalized tags)"""
    safe_name = name.lower()
    conf_path = Path(CONF_DIR) / f"{safe_name}.json"
    with open(conf_path) as f:
        conf = json.load(f)

    sc = conf.get("station_conf", {})
    schedule = {}
    for day in [
        "monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday", "sunday"
    ]:
        schedule[day] = {}
        for hour, slot in sc.get(day, {}).items():
            tags = slot.get("tags", [])
            if isinstance(tags, str):
                tags = [tags]
            schedule[day][hour] = {**slot, "tags": tags}
    return schedule


def replace_schedule(name: str, new_schedule: dict):
    """Replace full schedule"""
    safe_name = name.lower()
    conf_path = Path(CONF_DIR) / f"{safe_name}.json"
    with open(conf_path) as f:
        conf = json.load(f)

    sc = conf["station_conf"]
    sc.update(new_schedule)

    for day in [
        "monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday", "sunday"
    ]:
        for hour, slot in sc.get(day, {}).items():
            tags = slot.get("tags", [])
            if isinstance(tags, str):
                sc[day][hour]["tags"] = [tags]

    with open(conf_path, "w") as f:
        json.dump(conf, f, indent=2)
    return conf


def patch_slot(name: str, day: str, hour: int, slot: dict):
    """Patch one slot in schedule"""
    safe_name = name.lower()
    conf_path = Path(CONF_DIR) / f"{safe_name}.json"
    with open(conf_path) as f:
        conf = json.load(f)

    sc = conf.setdefault("station_conf", {})
    if day not in sc:
        sc[day] = {}

    tags = slot.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]

    sc[day][str(hour)] = {**slot, "tags": tags}

    with open(conf_path, "w") as f:
        json.dump(conf, f, indent=2)
    return conf


def reset_system():
    """Wipe and reinit"""
    shutil.rmtree(CATALOG_DIR, ignore_errors=True)
    shutil.rmtree(CONF_DIR, ignore_errors=True)
    os.makedirs(CATALOG_DIR, exist_ok=True)
    os.makedirs(CONF_DIR, exist_ok=True)
