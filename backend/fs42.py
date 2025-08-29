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


# ==== Helpers ====
def generate_conf(ch: dict):
    """
    ch is { "name": str, "config": { … } }
    Write a conf file wrapped as { "station_conf": { … } }
    """
    name = ch["name"]
    safe_name = name.lower()
    content_dir = f"catalog/{safe_name}"

    conf = {
        "station_conf": {
            "network_name": name,
            "channel_number": ch["config"].get("channel_number", 1),
            "network_type": ch["config"].get("network_type", "standard"),
            "tags": ch["config"].get("tags", []),
            "tag_colors": ch["config"].get("tag_colors", {}),
        }
    }
    sc = conf["station_conf"]

    nt = sc["network_type"]

    if nt == "standard":
        sc.update({
            "content_dir": content_dir,
            "commercial_dir": "commercial",
            "bump_dir": "bump",
            "schedule_increment": ch["config"].get("schedule_increment", 30),
            "break_strategy": ch["config"].get("break_strategy", "standard"),
            "commercial_free": ch["config"].get("commercial_free", False),
            "off_air_path": ch["config"].get("off_air_path", "runtime/off_air_pattern.mp4"),
            "signoff_path": ch["config"].get("signoff_path", "runtime/signoff.mp4"),
            "standby_image": ch["config"].get("standby_image", "runtime/standby.png"),
            "be_right_back_media": ch["config"].get("be_right_back_media", "runtime/brb.png"),
        })
        os.makedirs(Path(CATALOG_DIR) / safe_name / "commercials", exist_ok=True)
        os.makedirs(Path(CATALOG_DIR) / safe_name / "bump", exist_ok=True)

        # === Seed random weekly schedule ===
        available_tags = sc["tags"]
        for day in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]:
            sc[day] = {}
            for hour in range(24):
                if available_tags:
                    chosen = random.choice(available_tags)
                    sc[day][str(hour)] = {"tags": [chosen]}
                else:
                    sc[day][str(hour)] = {}  # off_air

    elif nt == "loop":
        sc.update({
            "content_dir": content_dir,
            "network_long_name": ch["config"].get("network_long_name", f"{name} Loop"),
            "loop_shuffle": ch["config"].get("loop_shuffle", True),
        })
        os.makedirs(Path(CATALOG_DIR) / safe_name, exist_ok=True)

    elif nt == "guide":
        sc.update({
            "runtime_dir": f"runtime/{safe_name}",
            "network_long_name": f"{name} Guide",
            "fullscreen": ch["config"].get("fullscreen", False),
            "width": ch["config"].get("width", 720),
            "height": ch["config"].get("height", 480),
            "window_decorations": ch["config"].get("window_decorations", False),
            "top_bg": ch["config"].get("top_bg", "blue3"),
            "bottom_bg": ch["config"].get("bottom_bg", "blue4"),
            "pad": ch["config"].get("pad", 10),
            "messages": ch["config"].get("messages", []),
            "message_rotation_rate": ch["config"].get("message_rotation_rate", 10),
            "message_fg": ch["config"].get("message_fg", "white"),
            "message_font_family": ch["config"].get("message_font_family", "Arial"),
            "message_font_size": ch["config"].get("message_font_size", 25),
            "images": ch["config"].get("images", []),
            "network_font_family": ch["config"].get("network_font_family", "Arial"),
            "network_font_size": ch["config"].get("network_font_size", 12),
            "schedule_font_family": ch["config"].get("schedule_font_family", "Arial"),
            "schedule_font_size": ch["config"].get("schedule_font_size", 12),
            "schedule_highlight_fg": ch["config"].get("schedule_highlight_fg", "yellow"),
            "schedule_fg": ch["config"].get("schedule_fg", "white"),
            "schedule_border_width": ch["config"].get("schedule_border_width", 4),
            "schedule_border_relief": ch["config"].get("schedule_border_relief", "raised"),
            "footer_messages": ch["config"].get("footer_messages", []),
            "footer_height": ch["config"].get("footer_height", 50),
            "schedule_row_count": ch["config"].get("schedule_row_count", 3),
            "normalize_title": ch["config"].get("normalize_title", True),
            "play_sound": ch["config"].get("play_sound", False),
            "sound_to_play": ch["config"].get("sound_to_play", ""),
        })

    elif nt == "streaming":
        sc.update({
            "runtime_dir": f"runtime/{safe_name}",
            "network_long_name": ch["config"].get("network_long_name", f"{name} Streaming"),
            "streams": ch["config"].get("streams", []),
        })

    elif nt == "web":
        sc.update({
            "web_url": ch["config"].get("web_url", "")
        })

    # Save
    conf_path = Path(CONF_DIR) / f"{safe_name}.json"
    with open(conf_path, "w") as f:
        json.dump(conf, f, indent=2)


def load_all_channels():
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

        name = sc["network_name"]
        safe_name = name.lower()
        result[name] = {
            "name": name,
            "path": sc.get("content_dir", str(CATALOG_DIR / safe_name)),
            "config": sc
        }
    return result


def delete_channel(name: str):
    safe_name = name.lower()
    conf_path = Path(CONF_DIR) / f"{safe_name}.json"
    if conf_path.exists():
        conf_path.unlink()
    cat_path = Path(CATALOG_DIR) / safe_name
    if cat_path.exists():
        shutil.rmtree(cat_path)


def get_schedule(name: str):
    safe_name = name.lower()
    conf_path = Path(CONF_DIR) / f"{safe_name}.json"
    with open(conf_path) as f:
        conf = json.load(f)

    sc = conf.get("station_conf", {})
    schedule = {}
    for day in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]:
        schedule[day] = {}
        for hour, slot in sc.get(day, {}).items():
            tags = slot.get("tags", [])
            if isinstance(tags, str):
                tags = [tags]
            schedule[day][hour] = {**slot, "tags": tags}
    return schedule


def replace_schedule(name: str, new_schedule: dict):
    safe_name = name.lower()
    conf_path = Path(CONF_DIR) / f"{safe_name}.json"
    with open(conf_path) as f:
        conf = json.load(f)

    sc = conf["station_conf"]
    sc.update(new_schedule)

    # normalize tags
    for day in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]:
        for hour, slot in sc.get(day, {}).items():
            tags = slot.get("tags", [])
            if isinstance(tags, str):
                sc[day][hour]["tags"] = [tags]

    with open(conf_path, "w") as f:
        json.dump(conf, f, indent=2)
    return conf


def patch_slot(name: str, day: str, hour: int, slot: dict):
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
    shutil.rmtree(CATALOG_DIR, ignore_errors=True)
    shutil.rmtree(CONF_DIR, ignore_errors=True)
    os.makedirs(CATALOG_DIR, exist_ok=True)
    os.makedirs(CONF_DIR, exist_ok=True)
