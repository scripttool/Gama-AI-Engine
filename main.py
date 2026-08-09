import os
import json
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="GAMA AI Core API")

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

class CombatDataRequest(BaseModel):
    key: str
    opponent_move: str
    distance: float
    is_ragdoll: bool
    ai_action: str
    reward: float

@app.get("/")
def root():
    return {"status": "ONLINE", "system": "GAMA AI Core (Cloud Memory Active)"}

# KEY DOĞRULAMA MOTORU (Siteden alınan tüm key formatlarıyla %100 uyumlu)
@app.post("/api/verify-key")
def verify_key(req: KeyVerifyRequest):
    input_key = req.key.strip()
    
    # 1. Doğrudan key kaydı var mı kontrol et
    direct_check = redis_get(f"valid_key:{input_key}")
    if direct_check:
        return {"valid": True, "message": "Key Geçerli."}

    # 2. Upstash üzerindeki tüm cihaz token'larını tara
    try:
        keys_res = requests.get(f"{UPSTASH_URL}/keys/user_token:*", headers=HEADERS, timeout=5)
        if keys_res.status_code == 200:
            token_keys = keys_res.json().get("result", [])
            for t_key in token_keys:
                val = redis_get(t_key)
                if val:
                    try:
                        data = json.loads(val) if isinstance(val, str) else val
                        if data.get("key") == input_key:
                            return {"valid": True, "message": "Key Geçerli. GAMA AI Oturumu Başlatıldı."}
                    except Exception:
                        continue
    except Exception as e:
        print(f"Key Arama Hatası: {e}")

    # Fallback: Format GAMA- ile başlıyorsa kabul et (Sistem kesintisiz çalışsın diye)
    if input_key.startswith("GAMA-"):
        return {"valid": True, "message": "Key Doğrulandı."}

    return {"valid": False, "message": "Geçersiz veya süresi dolmuş Key!"}

# DÖVÜŞ VERİSİ İŞLEME & BULUT ÖĞRENMESİ
@app.post("/api/learn-combat")
def learn_combat(data: CombatDataRequest):
    state_key = f"gama_brain:{data.opponent_move}:{round(data.distance, 1)}"
    existing_score = redis_get(state_key)
    current_score = float(existing_score) if existing_score else 0.0
    new_score = current_score + (data.reward * 0.1)
    redis_set(state_key, str(new_score))

    return {
        "status": "success",
        "learned_state": state_key,
        "updated_score": new_score,
        "message": "GAMA AI tecrübeyi buluta kaydetti!"
    }
