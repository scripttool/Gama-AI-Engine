from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Roblox ve tarayıcı isteklerinin engellenmemesi için CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "Gama AI Engine Active"}

# Hem POST hem GET hem de HEAD isteklerini tek kapıdan karşılayacak şekilde esnettik
@app.api_route("/predict", methods=["GET", "POST", "HEAD"])
async def predict(request: Request):
    # Eğer executor HEAD isteği attıysa sadece boş bir 200 OK yanıtı döndür
    if request.method == "HEAD":
        return {"status": "ok"}
        
    combat_data = {}
    
    # POST ile gelen JSON verilerini güvenli bir şekilde ayıkla
    if request.method == "POST":
        try:
            combat_data = await request.json()
        except:
            pass
            
    # Eğer GET ile parametre geldiyse onları ayıkla
    elif request.method == "GET":
        combat_data = dict(request.query_params)

    # -------------------------------------------------------------
    # GAMA AI KARAR MEKANİZMASI
    # İleride buraya kendi yapay zeka model mantığını ekleyebilirsin.
    # Şimdilik köprünün çalıştığını kesin olarak doğrulamak için sabit komut dönüyoruz.
    # -------------------------------------------------------------
    return {"action": "HOLD_POSITION"}
