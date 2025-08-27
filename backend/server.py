from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import fs42

app = FastAPI(
    title="FS42 Tsar Tools Backend",
    docs_url=None,
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== Models ====
class Channel(BaseModel):
    name: str
    path: str
    config: Dict[str, Any] = {}  # ✅ tags and tag_colors will live here

# In-memory store
channels: Dict[str, Channel] = {}

# ==== Startup ====
@app.on_event("startup")
def load_existing_channels():
    global channels
    channels = fs42.load_all_channels()
    print(f"[startup] Loaded {len(channels)} channels from confs/")

# ==== Routes ====
@app.get("/")
def root():
    return {"status": "FS42 Tsar Backend running", "endpoints": ["/channels", "/reset"]}

@app.get("/channels")
def list_channels():
    return list(channels.values())

@app.post("/channels")
def create_channel(ch: Channel):
    if ch.name in channels:
        raise HTTPException(status_code=400, detail="Channel already exists")
    channels[ch.name] = ch
    fs42.generate_conf(ch.dict())
    return ch

@app.get("/channels/{name}")
def get_channel(name: str):
    if name not in channels:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channels[name]

@app.put("/channels/{name}")
def update_channel(name: str, ch: Channel):
    if name not in channels:
        raise HTTPException(status_code=404, detail="Channel not found")

    # Support rename
    if ch.name != name:
        channels.pop(name, None)

    channels[ch.name] = ch
    fs42.generate_conf(ch.dict())
    return ch

@app.delete("/channels/{name}")
def delete_channel(name: str):
    if name not in channels:
        raise HTTPException(status_code=404, detail="Channel not found")
    fs42.delete_channel(name)
    channels.pop(name, None)
    return {"status": f"Channel {name} deleted"}

@app.get("/channels/{name}/schedule")
def get_schedule(name: str):
    if name not in channels:
        raise HTTPException(status_code=404, detail="Channel not found")
    return fs42.get_schedule(name)

@app.put("/channels/{name}/schedule")
def replace_schedule(name: str, new_schedule: Dict[str, Any]):
    if name not in channels:
        raise HTTPException(status_code=404, detail="Channel not found")
    return fs42.replace_schedule(name, new_schedule)

@app.patch("/channels/{name}/schedule/{day}/{hour}")
def patch_slot(name: str, day: str, hour: int, slot: Dict[str, Any]):
    if name not in channels:
        raise HTTPException(status_code=404, detail="Channel not found")
    return fs42.patch_slot(name, day, hour, slot)

@app.post("/reset")
def reset_system():
    fs42.reset_system()
    channels.clear()
    return {"status": "System reset"}
