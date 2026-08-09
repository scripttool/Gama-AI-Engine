import os
import json
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="GAMA AI Core - Live Decision Engine")

UPSTASH_URL = "https://splendid-buzzard-166843.upstash.io"
UPSTASH_TOKEN = "gQAAAAAAAou7AAIgcDFjNWFiYjNjNGUyMmI0YjQzOTViZTc3YWMyZmM3MjRkYg"

HEADERS = {
    "Authorization": f"Bearer {UPSTASH_TOKEN}"
}

def redis_get(key: str):
    try:
        response = requests.get(f"{UPSTASH_URL}/get/{key}", headers=HEADERS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("result")
    except Exception as e:
        print(f"Redis GET hatası: {e}")
    return None

def redis_set(key: str, value: str):
    try:
        requests.post(f"{UPSTASH_URL}/set/{key}", headers=HEADERS, data=value, timeout=5)
    except Exception as e:
        print(f"Redis SET hatası: {e}")

class KeyVerifyRequest(BaseModel):
    key: str

class LivePositionData(BaseModel):
    key: str
    my_position: dict # {"x": 10.5, "y": 3.0, "z": -45.2}
    enemy_position: dict # {"x": 15.0, "y": 3.0, "z": -40.0}
    enemy_velocity: dict # {"x": 1.2, "y": 0, "z": -5.0}

@app.get("/")
def root():
    return {"status": "ONLINE", "system": "GAMA AI Core (Command & Positioning Engine Active)"}

@app.post("/api/verify-key")
def verify_key(req: KeyVerifyRequest):
    input_key = req.key.strip()
    if input_key.startswith("GAMA-"):
        return {"valid": True, "message": "Key Doğrulandı. AI Merkezi Aktif."}
    return {"valid": False, "message": "Geçersiz Key!"}

# 🎯 CANLI KONUM ANALİZİ VE ANLIK KARAR ÜRETİCİ ENGINE
@app.post("/api/live-decision")
def live_decision(data: LivePositionData):
    # Düşmanın hareket vektörü ve mesafesini hesapla
    dx = data.enemy_position["x"] - data.my_position["x"]
    dz = data.enemy_position["z"] - data.my_position["z"]
    distance = (dx**2 + dz**2) ** 0.5

    # Gama AI Karar Algoritması
    target_pos = {
        "x": round(data.enemy_position["x"] + data.enemy_velocity["x"] * 0.5, 2),
        "y": data.enemy_position["y"],
        "z": round(data.enemy_position["z"] + data.enemy_velocity["z"] * 0.5, 2)
    }

    action = "APPROACH"
    if distance < 5.0:
        action = "BLOCK_AND_COUNTER"
    elif distance > 25.0:
        action = "PATROL_AND_SEARCH"

    response_payload = {
        "key": data.key,
        "action": action,
        "target_position": target_pos,
        "message": f"{data.key}, hedef konuma ({target_pos['x']}, {target_pos['z']}) hareket et ve '{action}' uygula!"
    }

    # Buluta o anki canlı durumu kaydet
    redis_set(f"live_state:{data.key}", json.dumps(response_payload))

    return response_payload
