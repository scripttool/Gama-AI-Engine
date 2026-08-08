import asyncio
import json
import sqlite3
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI()

# --- HAFIZA VERİTABANI ---
conn = sqlite3.connect("gama_memory.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS q_table (
        state TEXT, action TEXT, q_value REAL,
        PRIMARY KEY (state, action)
    )
""")
conn.commit()

ACTIONS = ["APPROACH", "RETREAT", "FLANK_LEFT", "FLANK_RIGHT", "ATTACK_M1", "BLOCK"]

def get_q_value(state, action):
    cursor.execute("SELECT q_value FROM q_table WHERE state = ? AND action = ?", (state, action))
    row = cursor.fetchone()
    return row[0] if row else 0.0

def update_q_value(state, action, new_q):
    cursor.execute("""
        INSERT INTO q_table (state, action, q_value)
        VALUES (?, ?, ?)
        ON CONFLICT(state, action) DO UPDATE SET q_value = excluded.q_value
    """, (state, action, new_q))
    conn.commit()

@app.get("/")
def home():
    return {"status": "GAMA AI Global Backend Active", "version": "2.0-WebSocket"}

# 📡 KİŞİYE ÖZEL KESİNTİSİZ WEBSOCKET ANTENİ
@app.websocket("/ws/{user_key}")
async def websocket_endpoint(websocket: WebSocket, user_key: str):
    await websocket.accept()
    print(f"📡 [GAMA-AI] Yeni Kullanıcı Bağlandı! Key: {user_key}")
    
    try:
        while True:
            # Roblox'tan gelen anlık 50Hz paketi oku
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)

            dist_status = "CLOSE" if data.get("enemy_distance", 999) < 12 else "FAR"
            threat_status = "THREAT" if (data.get("enemy_holding_item") or data.get("dangerous_asset_nearby")) else "CLEAR"
            state_str = f"{dist_status}_{threat_status}"

            # Q-Learning Stratejisi
            if random.random() < 0.15:
                chosen_action = random.choice(ACTIONS)
            else:
                q_values = {act: get_q_value(state_str, act) for act in ACTIONS}
                max_q = max(q_values.values())
                best_actions = [act for act, q in q_values.items() if q == max_q]
                chosen_action = random.choice(best_actions)

            nav_mode = "APPROACH"
            if chosen_action == "RETREAT" or threat_status == "THREAT":
                nav_mode = "RETREAT"
            elif chosen_action == "FLANK_LEFT":
                nav_mode = "FLANK_LEFT"

            # Kesintisiz yanıtı fırlat (HTTP gecikmesi yok!)
            response = {
                "user_key": user_key,
                "nav_mode": nav_mode,
                "action": chosen_action
            }
            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        print(f"❌ [GAMA-AI] Kullanıcı Ayrıldı: {user_key}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
