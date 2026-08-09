import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="GAMA AI Core API")

# Upstash Bulut Veritabanı Bilgileri
UPSTASH_URL = "https://splendid-buzzard-166843.upstash.io"
UPSTASH_TOKEN = "gQAAAAAAAou7AAIgcDFjNWFiYjNjNGUyMmI0YjQzOTViZTc3YWMyZmM3MjRkYg"

HEADERS = {
    "Authorization": f"Bearer {UPSTASH_TOKEN}"
}

# Upstash Yardımcı Fonksiyonları
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

# Veri Modelleri
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

# 1. Roblox Key Doğrulama Endpoint'i
@app.post("/api/verify-key")
def verify_key(req: KeyVerifyRequest):
    try:
        res = requests.get(f"{UPSTASH_URL}/sismember/active_keys/{req.key}", headers=HEADERS, timeout=5)
        if res.status_code == 200 and res.json().get("result") == 1:
            return {"valid": True, "message": "Key geçerli. GAMA AI Oturumu Başlatıldı."}
    except Exception as e:
        print(f"Key doğrulama hatası: {e}")

    return {"valid": False, "message": "Geçersiz veya süresi dolmuş Key!"}

# 2. Dövüş Verisi İşleme & Öğrenme (Kalıcı Bulut Hafızası)
@app.post("/api/learn-combat")
def learn_combat(data: CombatDataRequest):
    key_check = verify_key(KeyVerifyRequest(key=data.key))
    if not key_check.get("valid"):
        raise HTTPException(status_code=401, detail="Geçersiz Key!")

    # AI Öğrenme Hafızası Kaydı
    state_key = f"gama_brain:{data.opponent_move}:{round(data.distance, 1)}"
    
    existing_score = redis_get(state_key)
    current_score = float(existing_score) if existing_score else 0.0
    
    # Tecrübe güncellemesi
    new_score = current_score + (data.reward * 0.1)
    
    # Bulut hafızasına kaydet
    redis_set(state_key, str(new_score))

    return {
        "status": "success",
        "learned_state": state_key,
        "updated_score": new_score,
        "message": "GAMA AI tecrübeyi buluta kaydetti!"
    }
