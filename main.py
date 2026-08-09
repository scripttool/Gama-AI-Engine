import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Tüm Platformlar İçin Tam İzin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FrameData(BaseModel):
    my_position: dict
    enemy_position: dict
    is_teacher_mode: bool
    human_action: str

@app.get("/")
def read_root():
    return {"status": "Gama AI Universal Engine Online"}

# 100 Hz Universal Pipeline Endpoint
@app.post("/api/v1/stream")
async def stream_pipeline(data: FrameData):
    # Otonom Mantık İşleme (Örnek Tepki Mantığı)
    action = "IDLE"
    target_pos = data.enemy_position

    # Eğer düşman yakınsa ve AI Modundaysa
    if not data.is_teacher_mode:
        action = "ATTACK_COUNTER"

    return {
        "status": "OK",
        "action": action,
        "target_position": target_pos
    }
