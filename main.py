import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

# WebSocket Bağlantı Yöneticisi
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

manager = ConnectionManager()

@app.get("/")
def read_root():
    return {"status": "Gama AI Engine 100Hz WSS Online"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Roblox'tan 10ms'de bir gelen canlı veriyi oku (0 ms gecikme)
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)

            # 100 Hz Canlı Analiz
            my_pos = data.get("my_position", {"x": 0, "y": 0, "z": 0})
            enemy_pos = data.get("enemy_position", {"x": 0, "y": 0, "z": 0})
            is_teacher = data.get("is_teacher_mode", True)
            action_type = data.get("human_action", "NONE")

            # 1. ÖĞRET MEN MODU (İnsan Hareketlerini Kaydetme)
            if is_teacher:
                if action_type != "NONE":
                    # İnsan girdisi buluta / hafızaya işlenir
                    pass
                response = {"status": "RECORDING"}

            # 2. OTONOM MOD (10ms Anlık Karar Motoru)
            else:
                dx = enemy_pos["x"] - my_pos["x"]
                dz = enemy_pos["z"] - my_pos["z"]
                dist = (dx**2 + dz**2)**0.5

                decision = "IDLE"
                if dist > 0 and dist <= 8:
                    decision = "BLOCK_AND_COUNTER"
                elif dist > 8 and dist <= 25:
                    decision = "APPROACH"

                response = {
                    "action": decision,
                    "target_position": enemy_pos if decision == "APPROACH" else None
                }

            # Kararı anında tünelden Roblox'a fırlat
            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)
