# --- KONFIGURASI Color & STYLE ---
COLOR_MAIN_BG = "#131316"      
COLOR_SIDEBAR = "#1c1c21"      
COLOR_BUBBLE_USER = "#a855f7"   
COLOR_BUBBLE_AI = "#25252b"     
COLOR_ACCENT = "#a855f7"       
COLOR_TEXT = "#e1e1e6"        
COLOR_SUBTEXT = "#9494b8"      
COLOR_BORDER = "#2d2d35"       

STYLE_SHEET = f"""
    QMainWindow {{ 
        background-color: {COLOR_MAIN_BG}; 
    }}
    
    QWidget {{
        color: {COLOR_TEXT};
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }}

    #Sidebar {{ 
        background-color: {COLOR_SIDEBAR}; 
        border-right: 1px solid {COLOR_BORDER};
    }}

    #ChatDisplay {{ 
        background-color: transparent; 
        border: none;
    }}

    /* ScrollBar Styling */
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 8px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: #3f3f46;
        min-height: 20px;
        border-radius: 4px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
    }}

    /* Input & Fields */
    QLineEdit {{
        background-color: #25252b;
        border: 1px solid #3f3f46;
        border-radius: 10px;
        padding: 10px 15px;
        color: white;
        font-size: 14px;
    }}
    QLineEdit:focus {{
        border: 1px solid {COLOR_ACCENT};
    }}

    #InputContainer {{
        background-color: #25252b;
        border: 1px solid {COLOR_BORDER};
        border-radius: 24px;
        margin: 10px 20px 20px 20px;
        padding: 4px 8px;
    }}

    #InputBox {{
        background-color: transparent;
        border: none;
        padding: 10px;
        font-size: 15px;
    }}

    /* Buttons */
    QPushButton {{
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: #2d2d35;
    }}

    #PrimaryBtn {{
        background-color: {COLOR_ACCENT};
        color: white;
    }}
    #PrimaryBtn:hover {{
        background-color: #9333ea;
    }}

    #NewChatBtn {{
        background-color: transparent;
        color: {COLOR_TEXT};
        border-radius: 20px;
        padding: 10px 15px;
        font-size: 14px;
        font-weight: 500;
        text-align: left;
    }}
    #NewChatBtn:hover {{
        background-color: #2d2d35;
    }}

    /* Table Widget */
    QTableWidget {{
        background-color: {COLOR_SIDEBAR};
        alternate-background-color: #25252b;
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        gridline-color: transparent;
        outline: none;
    }}
    QHeaderView::section {{
        background-color: #1a1a1f;
        color: {COLOR_SUBTEXT};
        padding: 12px;
        border: none;
        font-weight: bold;
        text-transform: uppercase;
        font-size: 11px;
    }}
    QTableWidget::item {{
        padding: 12px;
        border-bottom: 1px solid {COLOR_BORDER};
    }}
    QTableWidget::item:selected {{
        background-color: #2d2d35;
        color: white;
    }}

    /* Labels & Headers */
    QLabel {{
        color: {COLOR_TEXT};
    }}
    .SubText {{
        color: {COLOR_SUBTEXT};
        font-size: 12px;
    }}
    .HeaderTitle {{
        color: white;
        font-size: 20px;
        font-weight: bold;
    }}

    /* Cards */
    #Card {{
        background-color: #1c1c21;
        border: 1px solid {COLOR_BORDER};
        border-radius: 16px;
    }}
    #Card:hover {{
        background-color: #25252b;
        border: 1px solid {COLOR_ACCENT};
    }}
    #AIBubble:hover {{
        background-color: #25252b;
        border: 1px solid {COLOR_ACCENT};
    }}

    /* Chat Bubbles */
    #UserBubble {{
        background-color: {COLOR_BUBBLE_USER};
        border-radius: 18px;
    }}
    #UserBubble QLabel {{
        color: white;
        font-size: 14px;
        background-color: transparent;
    }}

    #AIBubble {{
        background-color: {COLOR_BUBBLE_AI};
        border: 1px solid {COLOR_BORDER};
        border-radius: 18px;
    }}
    #AIBubble QLabel {{
        color: {COLOR_TEXT};
        font-size: 14px;
        background-color: transparent;
    }}

    #UserAvatar {{
        font-size: 24px;
        background-color: transparent;
    }}
    #AIAvatar {{
        font-size: 20px;
        background-color: #1a1a1f;
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        padding: 5px;
    }}

    #LoadingAnim {{
        color: {COLOR_ACCENT};
        font-style: italic;
        font-size: 13px;
        margin-left: 55px;
        margin-top: 5px;
        margin-bottom: 5px;
    }}

    #HeaderChat {{
        background-color: {COLOR_SIDEBAR};
        border-bottom: 1px solid {COLOR_BORDER};
    }}

    #RightSidebar {{
        background-color: {COLOR_SIDEBAR};
        border-left: 1px solid {COLOR_BORDER};
    }}

    /* Input Accessories */
    #IconButton {{
        font-size: 18px;
        color: {COLOR_SUBTEXT};
        background: transparent;
        border: none;
    }}
    #IconButton:hover {{
        color: white;
    }}

    /* Special Buttons */
    #DangerBtn {{
        background-color: #ef4444;
        color: white;
    }}
    #SuccessBtn {{
        background-color: #10b981;
        color: white;
    }}

    /* Calendar Widget */
    QCalendarWidget QWidget {{ 
        alternate-background-color: #25252b; 
    }}
    QCalendarWidget QToolButton {{ 
        color: white; 
        background-color: transparent; 
    }}
    QCalendarWidget QMenu {{ 
        background-color: #25252b; 
        color: white; 
    }}
    QCalendarWidget QSpinBox {{ 
        background-color: #25252b; 
        color: white; 
    }}
    QCalendarWidget QAbstractItemView:enabled {{ 
        background-color: {COLOR_SIDEBAR}; 
        color: white; 
        selection-background-color: {COLOR_ACCENT}; 
        selection-color: white; 
    }}
    QCalendarWidget QAbstractItemView:disabled {{ 
        color: #52525b; 
    }}
"""
