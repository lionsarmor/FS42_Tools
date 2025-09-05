import os
import json
import shutil
import random
from pathlib import Path

# === Base paths ===
ROOT = Path(__file__).resolve().parents[1] / "FieldStation42"
CATALOG_DIR = ROOT / "catalog"
CONF_DIR = ROOT / "confs"

CATALOG_DIR.mkdir(parents=True, exist_ok=True)
CONF_DIR.mkdir(parents=True, exist_ok=True)

# === Baselines ===
GUIDE_BASELINE_CONF = {
    "network_name": "Guide",
    "channel_number": 1,
    "network_type": "guide",
    "runtime_dir": "runtime/guide",

    "play_sound": True,
    "sound_to_play": "runtime/guide/background.mp3",

    # Window / layout
    "fullscreen": True,
    "width": 1920,
    "height": 1080,
    "window_decorations": False,
    "top_bg": "blue3",
    "bottom_bg": "blue4",
    "pad": 20,

    # Messages / images
    "messages": [
        "FieldStation42\nCable Entertainment",
        "Cheers!\nFrom us to you!",
        "FieldStation42 Guide\nOn cable mode."
    ],
    "images": [
        "runtime/guide/image0.png",
        "runtime/guide/image1.png",
        "runtime/guide/image2.png"
    ],
    "footer_messages": [
        "You are watching FieldStation42",
        "Now with cable mode."
    ],

    # Message appearance
    "message_rotation_rate": 10,
    "message_fg": "white",
    "message_font_family": "Arial",
    "message_font_size": 32,

    # Fonts for other areas
    "network_font_family": "Arial",
    "network_font_size": 20,
    "schedule_font_family": "Arial",
    "schedule_font_size": 20,

    # Schedule colors / borders
    "schedule_highlight_fg": "yellow",
    "schedule_fg": "white",
    "schedule_border_width": 4,
    "schedule_border_relief": "raised",

    # Footer
    "footer_height": 100,

    # Options
    "schedule_row_count": 3,
    "normalize_title": True,
}


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
    "commercial_free": True,
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

WEATHER_BASELINE_CONF = {
    "network_name": "",
    "channel_number": 1,
    "network_type": "weather",

    # The only thing FS42 actually reads is this final web_url.
    # All checkbox values from `options` must be baked into this string by the frontend before saving.
    "web_url": "",

    # Stored for convenience in the editor UI (not used by FS42 at runtime).
    "ip": "127.0.0.1",
    "location": "",

    # UI-only metadata that frontend uses to assemble `web_url`
    "options": {
        "hazards": False,
        "current-weather": False,
        "latest-observations": False,
        "hourly": False,
        "hourly-graph": False,
        "travel": False,
        "regional-forecast": False,
        "local-forecast": False,
        "extended-forecast": False,
        "almanac": False,
        "spc-outlook": False,
        "radar": False,
    },

    "settings": {
        "units": "us",
        "speed": 1.0,
        "kiosk": True,
        "autoplay": True,
    },
}



# === Helpers ===
def _baseline_for_type(network_type: str) -> dict:
    if network_type == "guide":
        return dict(GUIDE_BASELINE_CONF)
    elif network_type in ("weather", "web", "diagnostic"):
        return dict(WEATHER_BASELINE_CONF)
    else:
        return dict(BASELINE_CONF)

def _generate_default_schedule(tags, increment=30):
    """Generate a default 7-day schedule using provided tags."""
    if not tags:
        return {}
    days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    schedule = {}
    for day in days:
        schedule[day] = {}
        for hour in range(24):
            tag = random.choice(tags)
            schedule[day][str(hour)] = {"tags": [tag]}
    return schedule

# === Core functions ===
def generate_conf(ch: dict, old_name: str = None):
    """
    Generate or update a channel config.
    If old_name is provided (edit), delete the old entry and replace with new.
    """
    name = ch.get("name") or ch.get("config", {}).get("network_name") or "UnnamedChannel"
    safe_name = name.lower()
    user_conf = ch.get("config", {})
    ntype = user_conf.get("network_type", "standard")

    # If renaming → delete old config first
    if old_name and old_name.lower() != safe_name:
        old_conf_path = Path(CONF_DIR) / f"{old_name.lower()}.json"
        if old_conf_path.exists():
            old_conf_path.unlink()
        old_cat = Path(CATALOG_DIR) / old_name.lower()
        if old_cat.exists() and not any(old_cat.iterdir()):
            shutil.rmtree(old_cat)

    # === Weather/Web/Diagnostic/Streaming (pass-through) ===
    if ntype in ["weather", "web", "diagnostic", "streaming"]:
        sc = {
            "network_name": user_conf.get("network_name", name),
            "channel_number": user_conf.get("channel_number", 1),
            "network_type": "web",
            "web_url": user_conf.get("web_url", ""),
        }

    # === Standard channels ===
    elif ntype == "standard":
        sc = dict(BASELINE_CONF)
        sc.update(user_conf)
        sc["network_name"] = name

        content_dir = f"catalog/{safe_name}"
        sc["content_dir"] = content_dir
        os.makedirs(Path(content_dir), exist_ok=True)
        os.makedirs(Path(CATALOG_DIR) / safe_name / "commercial", exist_ok=True)
        os.makedirs(Path(CATALOG_DIR) / safe_name / "bump", exist_ok=True)

        # Ensure tag folders
        for tag in sc.get("tags", []):
            os.makedirs(Path(CATALOG_DIR) / safe_name / tag, exist_ok=True)

        # Generate schedule if missing
        if not any(sc.get(day) for day in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]):
            sc.update(_generate_default_schedule(sc.get("tags", []), sc.get("schedule_increment", 30)))

    # === Loop channels ===
    elif ntype == "loop":
        sc = dict(BASELINE_CONF)
        sc.update(user_conf)
        sc["network_name"] = name
        sc.setdefault("runtime_dir", f"runtime/{safe_name}")
        sc.setdefault("content_dir", f"catalog/{safe_name}")
        os.makedirs(Path(sc["content_dir"]), exist_ok=True)

    # === Guide channel ===
    elif ntype == "guide":
        sc = dict(GUIDE_BASELINE_CONF)
        sc.update(user_conf)
        sc["network_name"] = name

    else:
        # Fallback to baseline
        sc = _baseline_for_type(ntype)
        sc.update(user_conf)
        sc["network_name"] = name

    # Save clean JSON under new name
    conf_path = Path(CONF_DIR) / f"{safe_name}.json"
    with open(conf_path, "w") as f:
        json.dump({"station_conf": sc}, f, indent=2)


def load_all_channels():
    result = {}
    if not os.path.exists(CONF_DIR):
        return result
    for fn in os.listdir(CONF_DIR):
        if not fn.endswith(".json") or fn.startswith("."):
            continue
        try:
            with open(os.path.join(CONF_DIR, fn)) as f:
                data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load {fn}: {e}")
            continue
        sc = data.get("station_conf")
        if not sc:
            continue
        merged = _baseline_for_type(sc.get("network_type"))
        merged.update(sc)
        name = merged.get("network_name") or fn.replace(".json", "")
        safe_name = name.lower()
        result[name] = {
            "name": name,
            "path": merged.get("content_dir", str(CATALOG_DIR / safe_name)),
            "config": merged
        }
        conf_path = Path(CONF_DIR) / fn
        with open(conf_path, "w") as f:
            json.dump({"station_conf": merged}, f, indent=2)
    return result


def delete_channel(name: str):
    safe_name = name.lower()

    # Delete config file (case-insensitive match)
    for fn in os.listdir(CONF_DIR):
        if fn.lower() == f"{safe_name}.json":
            (Path(CONF_DIR) / fn).unlink()
            break

    # Delete catalog dir if empty
    cat_path = Path(CATALOG_DIR) / safe_name
    if cat_path.exists() and cat_path.is_dir() and not any(cat_path.iterdir()):
        shutil.rmtree(cat_path)


def get_schedule(name: str):
    safe_name = name.lower()
    conf_path = Path(CONF_DIR) / f"{safe_name}.json"
    with open(conf_path) as f:
        conf = json.load(f)
    sc = conf.get("station_conf", {})
    return {
        day: {
            h: {"tags": v.get("tags", []) if isinstance(v.get("tags", []), list) else [v.get("tags")]}
            for h, v in sc.get(day, {}).items()
        }
        for day in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    }


def replace_schedule(name: str, new_schedule: dict):
    safe_name = name.lower()
    conf_path = Path(CONF_DIR) / f"{safe_name}.json"
    with open(conf_path) as f:
        conf = json.load(f)
    sc = conf["station_conf"]
    sc.update(new_schedule)
    with open(conf_path, "w") as f:
        json.dump(conf, f, indent=2)
    return conf

def patch_slot(name: str, day: str, hour: int, slot: dict):
    safe_name = name.lower()
    conf_path = Path(CONF_DIR) / f"{safe_name}.json"

    with open(conf_path) as f:
        conf = json.load(f)

    sc = conf.setdefault("station_conf", {})
    sc.setdefault(day, {})

    # === Tags / special ===
    if slot.get("special"):
        tags = [slot["special"].strip()]
    else:
        tags = slot.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]

    # Ensure tag folders + add to station_conf.tags
    content_dir = sc.get("content_dir", f"catalog/{safe_name}")
    base_path = Path(content_dir)
    if not base_path.is_absolute():
        base_path = CATALOG_DIR / Path(content_dir).name

    for tag in tags:
        if tag not in ("off_air", "signoff", "commercial", "bump", ""):
            os.makedirs(base_path / tag, exist_ok=True)
            if tag not in sc.get("tags", []):
                sc.setdefault("tags", []).append(tag)

    # Save slot
    sc[day][str(hour)] = {
        "tags": tags,
        "start_bump": slot.get("start_bump", ""),
        "end_bump": slot.get("end_bump", ""),
        "commercial_break": slot.get("commercial_break", False),
        "duration_override": slot.get("duration_override", None),
        "notes": slot.get("notes", "")
    }

    with open(conf_path, "w") as f:
        json.dump(conf, f, indent=2)

    return conf
