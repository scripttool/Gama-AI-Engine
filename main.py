from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import uuid

# Sunucunun ana objesi. Uvicorn doğrudan bu "app" değişkenini arar.
app = FastAPI(title="Gama AI - Battlegrounds Engine")

# Canlı oyun odaları havuzu
game_sessions: Dict[str, dict] = {}

class KeyRequest(BaseModel):
    discord_id: str

class GameData(BaseModel):
    gama_key: str
    my_x: float
    my_y: float
    my_z: float
    enemy_x: float
    enemy_y: float
    enemy_z: float
    enemy_health: float
    enemy_state: str

@app.post("/generate-key")
async def generate_key(request: KeyRequest):
    new_key = f"GAMA-{str(uuid.uuid4())[:8]}"
    game_sessions[new_key] = {
        "discord_id": request.discord_id,
        "latest_action": "WAITING_FOR_GAME",
        "enemy_distance": 0.0
    }
    return {"gama_key": new_key, "status": "Ready"}

@app.post("/update-game")
async def update_game(data: GameData):
    if data.gama_key not in game_sessions:
        raise HTTPException(status_code=404, detail="Gecersiz Gama-Key!")
    
    distance = ((data.enemy_x - data.my_x)**2 + 
                (data.enemy_y - data.my_y)**2 + 
                (data.enemy_z - data.my_z)**2)**0.5
    
    action = "HOLD_POSITION"
    
    if data.enemy_state == "Ragdoll":
        action = "FORWARD_DASH + M1_COMBO"
    elif distance <= 5.0:
        if data.enemy_state == "Attacking":
            action = "PERFECT_BLOCK"
        else:
            action = "M1_COMBO_START"
    elif distance > 5.0 and distance <= 15.0:
        action = "APPROACH_ENEMY"
        
    game_sessions[data.gama_key]["enemy_distance"] = round(distance, 2)
    game_sessions[data.gama_key]["latest_action"] = action
    
    return {"action": action, "distance": round(distance, 2)}

@app.get("/session-status/{gama_key}")
async def get_status(gama_key: str):
    if gama_key not in game_sessions:
        return {"status": "Offline"}
    return game_sessions[gama_key]
