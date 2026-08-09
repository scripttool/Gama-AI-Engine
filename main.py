from fastapi import FastAPI, Request
import math

app = FastAPI()

# Ana Gama AI Beyni ve Dünya Hafızası
GAME_BRAIN = {
    "learned_patterns": {},  # Oyunculardan öğrenilen dersler
    "active_mode": "OPTIMUM"  # Varsayılan mod: OPTIMUM (İstenirse RADIUM yapılır)
}

def analyze_observed_players(players_data):
    """
    Sunucudaki tüm oyuncuları izler, hatalarından ve doğrularından ders çıkarır.
    """
    for player in players_data:
        p_id = player.get("player_id")
        hp_change = player.get("hp_change", 0)
        state = player.get("state")
        action = player.get("action_detected")
        
        # HATA TESPİTİ (Eksi Puan / Yanlış Hamle)
        if hp_change < 0 and state == "Ragdoll" and action != "KEY_Q":
            # Bir oyuncu Ragdoll durumunda Q basmayıp hasar yedi!
            # AI bunu olumsuz bir ders olarak kaydeder:
            GAME_BRAIN["learned_patterns"]["ragdoll_no_q_penalty"] = -1.0
            
        # BAŞARI TESPİTİ (Artı Puan / Mükemmel Hamle)
        elif hp_change == 0 and action == "BLOCK_F" and state == "Attacked":
            GAME_BRAIN["learned_patterns"]["perfect_block_reward"] = +1.0


@app.post("/pipeline")
async def universal_pipeline(request: Request):
    data = await request.json()
    user_id = data.get("user_id", "UNKNOWN")
    selected_mode = data.get("mode", "OPTIMUM") # RADIUM veya OPTIMUM
    
    # 1. İZLEYİCİ MODU: Sunucudaki herkesin verisini işle ve ders çıkar
    if "observed_players" in data:
        analyze_observed_players(data["observed_players"])
        
    # 2. GAMA MODEL SEÇİMİ (Duyu Odak Uzayı)
    my_data = data.get("my_data", {})
    nearby_objects = data.get("nearby_objects", [])
    
    if selected_mode == "RADIUM":
        # Radium Modu: Haritadaki TÜM objeleri vektörel işleme al
        # (Teleskop Görüşü)
        processed_grid = nearby_objects # Tüm harita objeleri
    else:
        # Optimum Modu: Sadece yakın dövüş mesafesindeki 50 stud içi objeleri süz
        # (Dürbün / Keskin Nişancı Görüşü)
        processed_grid = [obj for obj in nearby_objects if obj.get("dist", 999) < 50]

    # 3. AKSİYON ÇIKTISI (Klavyeye Verilecek Komut)
    # Şimdilik dinamik idrak çıktısını simüle ediyoruz:
    action_output = {
        "status": "ACTIVE",
        "mode_used": selected_mode,
        "learned_state_count": len(GAME_BRAIN["learned_patterns"]),
        "execute_command": "IDLE" # Veya "PRESS_Q", "ATTACK_M1", "BLOCK_F"
    }
    
    # Eğer oyuncu fırlatıldıysa ve izleyici modunda bundan ders çıkardıysa:
    if my_data.get("state") == "Ragdoll":
        action_output["execute_command"] = "PRESS_Q"
        
    return action_output
