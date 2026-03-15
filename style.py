# --- KONFIGURASI WARNA & STYLE ---
COLOR_MAIN_BG = "#131316"      # Background gelap pekat
COLOR_SIDEBAR = "#1c1c21"      # Sidebar sedikit lebih terang
COLOR_BUBBLE_AI = "#31244e"    # Purple gelap untuk AI
COLOR_ACCENT = "#a855f7"       # Ungu terang (Tombol & Icon)
COLOR_TEXT = "#e1e1e6"         # Teks terang

STYLE_SHEET = f"""
    QMainWindow {{ background-color: {COLOR_MAIN_BG}; }}
    
    #Sidebar {{ 
        background-color: {COLOR_SIDEBAR}; 
        border-right: 1px solid #2d2d35;
    }}

    #ChatDisplay {{ 
        background-color: transparent; 
        border: none;
        color: {COLOR_TEXT};
    }}

    #InputContainer {{
        background-color: #25252b;
        border-radius: 20px;
        padding: 5px;
        margin: 10px;
    }}

    #InputBox {{ 
        background-color: transparent; 
        border: none; 
        color: white;
        padding: 10px;
        font-size: 14px;
    }}

    #NewChatBtn {{
        background: linear-gradient(to right, #a855f7, #7c3aed);
        background-color: {COLOR_ACCENT};
        color: white;
        border-radius: 12px;
        padding: 12px;
        font-weight: bold;
    }}

    QLabel {{ color: #9494b8; font-size: 13px; }}
"""
