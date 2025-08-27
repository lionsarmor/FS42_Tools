import os
import json
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
CATALOG_DIR = os.path.join(os.path.dirname(ROOT), "catalog")
CONF_DIR = os.path.join(os.path.dirname(ROOT), "confs")

os.makedirs(CATALOG_DIR, exist_ok=True)
os.makedirs(CONF_DIR, exist_ok=True)


# ==== Helpers ====
import random

def generate_conf(ch: dict):
    name = ch["name"]
    path = ch["path"]

    conf = {
        "station_conf": {
            "network_name": name,
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
            "bump_dir": os.path.join(path, "bumps"),
            "schedule_increment": ch["config"].get("schedule_increment", 30),
            "break_strategy": ch["config"].get("break_strategy", "standard"),
        })
        os.makedirs(os.path.join(path, "shows"), exist_ok=True)
        os.makedirs(os.path.join(path, "movies"), exist_ok=True)
        os.makedirs(os.path.join(path, "commercials"), exist_ok=True)
        os.makedirs(os.path.join(path, "bumps"), exist_ok=True)

        # === ✅ Seed random weekly schedule ===
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
            "network_long_name": ch["config"].get("network_long_name", f"{name} Loop")
        })
        os.makedirs(path, exist_ok=True)

    elif nt == "streaming":
        conf["station_conf"].update({
            "runtime_dir": ch["config"].get("runtime_dir", f"runtime/{name}"),
            "network_long_name": ch["config"].get("network_long_name", f"{name} Streaming"),
            "streams": ch["config"].get("streams", []),
        })

    elif nt == "web":
        conf["station_conf"].update({
            "web_url": ch["config"].get("web_url", "")
        })

    # Save conf
    with open(os.path.join(CONF_DIR, f"{name}.json"), "w") as f:
        json.dump(conf, f, indent=2)



def load_all_channels():
    """
    Load all channels from confs/ into a dict keyed by channel name.
    """
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
        result[name] = {
            "name": name,
            "path": data["station_conf"].get("content_dir", f"catalog/{name}"),
            "config": data["station_conf"],  # includes tags + tag_colors
        }
    return result


def delete_channel(name: str):
    conf_path = os.path.join(CONF_DIR, f"{name}.json")
    if os.path.exists(conf_path):
        os.remove(conf_path)
    cat_path = os.path.join(CATALOG_DIR, name)
    if os.path.exists(cat_path):
        shutil.rmtree(cat_path)


def get_schedule(name: str):
    conf_path = os.path.join(CONF_DIR, f"{name}.json")
    with open(conf_path) as f:
        conf = json.load(f)
    return {
        day: conf["station_conf"].get(day, {})
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    }


def replace_schedule(name: str, new_schedule: dict):
    conf_path = os.path.join(CONF_DIR, f"{name}.json")
    with open(conf_path) as f:
        conf = json.load(f)
    conf["station_conf"].update(new_schedule)
    with open(conf_path, "w") as f:
        json.dump(conf, f, indent=2)
    return conf


def patch_slot(name: str, day: str, hour: int, slot: dict):
    conf_path = os.path.join(CONF_DIR, f"{name}.json")
    with open(conf_path) as f:
        conf = json.load(f)
    if day not in conf["station_conf"]:
        conf["station_conf"][day] = {}
    conf["station_conf"][day][str(hour)] = slot
    with open(conf_path, "w") as f:
        json.dump(conf, f, indent=2)
    return conf


def reset_system():
    shutil.rmtree(CATALOG_DIR, ignore_errors=True)
    shutil.rmtree(CONF_DIR, ignore_errors=True)
    os.makedirs(CATALOG_DIR, exist_ok=True)
    os.makedirs(CONF_DIR, exist_ok=True)
