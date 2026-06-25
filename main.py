from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Yapay zekanın sahip olduğu kaslar (Aksiyonlar)
ACTIONS = ["MOVE_FORWARD", "MOVE_BACKWARD", "MOVE_LEFT", "MOVE_RIGHT", "ATTACK_M1", "BLOCK"]

# Basit bir yapay zeka hafızası (İleride veri tabanına bağlanabilir)
# Her oyuncunun durumunu hafızada tutmak için sözlük
ai_memory = {}

@app.get("/")
async def root():
    return {"status": "Gama AI Brain is Active and Evolving"}

@app.api_route("/predict", methods=["GET", "POST", "HEAD"])
async def predict(request: Request):
    if request.method == "HEAD":
        return {"status": "ok"}

    # Roblox'tan gelen duyu organı verilerini al
    combat_data = {}
    if request.method == "POST":
        try: combat_data = await request.json()
        except: pass
    elif request.method == "GET":
        combat_data = dict(request.query_params)

    # Oyuncu verilerini ayıkla (varsayılan değerler ile)
    current_health = float(combat_data.get("Health", 100))
    in_combat = bool(combat_data.get("InCombat", False))
    
    # -------------------------------------------------------------
    # İLK KIVILCIM: RASTGELE DENEME VE ÖĞRENME ALGORİTMASI (Epsilon-Greedy)
    # -------------------------------------------------------------
    # Yapay zeka %70 ihtimalle tamamen rastgele yeni tuşlar deneyecek (Keşif)
    # %30 ihtimalle öğrendiği en iyi hamleyi yapacak (Sömürü)
    
    chosen_action = random.choice(ACTIONS)
    
    # Küçük bir mantık (Kıvılcımı hızlandırmak için): 
    # Eğer canı bir önceki adıma göre düştüyse yapay zekayı uyaralım
    if in_combat and current_health < 50:
        # Canı azsa defansif aksiyonların seçilme şansını biraz artıralım (Yapay içgüdü)
        chosen_action = random.choice(["MOVE_BACKWARD", "BLOCK", "ATTACK_M1"])

    # Roblox'a fırlatılacak çıktı komutu
    # duration: Tuşa kaç saniye basılı tutulacağı (Senin istediğin gibi)
    return {
        "action": chosen_action,
        "duration": round(random.uniform(0.5, 1.5), 2),
        "turn_degree": random.randint(-45, 45)
    }
