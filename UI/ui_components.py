from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QScrollArea, QLineEdit, QPushButton, 
                             QComboBox, QStackedWidget, QDialog, QTableWidget, 
                             QHeaderView, QCalendarWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor
from UI.style import STYLE_SHEET, COLOR_ACCENT
from ai_integration.ai_engine import get_models

class LoadingAnimation(QLabel):
    def __init__(self):
        super().__init__()
        self.setObjectName("LoadingAnim")
        self.setText("Bot is typing...")
        self.hide()

class ProfileSetupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to Ollama Vision")
        self.setFixedSize(450, 380)
        self.setStyleSheet(STYLE_SHEET)
        
        self.user_name = "User"
        self.user_role = "AI ENTHUSIAST"
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        lbl_title = QLabel("<h1 style='color: white; margin: 0; font-size: 26px;'>Setup Your Profile</h1>")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)
        
        # Name Input
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Enter your name...")
        layout.addWidget(QLabel("<b style='color:#e1e1e6; font-size: 16px;'>Name:</b>"))
        layout.addWidget(self.input_name)
        
        # Role Input
        self.input_role = QLineEdit()
        self.input_role.setPlaceholderText("Enter your role/profession...")
        layout.addWidget(QLabel("<b style='color:#e1e1e6; font-size: 16px;'>Role:</b>"))
        layout.addWidget(self.input_role)
        
        # Start Button
        btn_start = QPushButton("Start Chatting")
        btn_start.setObjectName("PrimaryBtn")
        btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_start.clicked.connect(self.accept_data)
        layout.addWidget(btn_start)
        layout.addStretch()

    def accept_data(self):
        name = self.input_name.text().strip()
        role = self.input_role.text().strip()
        if name: self.user_name = name
        if role: self.user_role = role.upper()
        self.accept()

class MainInterface(QMainWindow):
    # Signals for communication with controller (app.py)
    send_message_signal = pyqtSignal(str, str) # text, image_path
    new_chat_signal = pyqtSignal()
    toggle_sidebar_signal = pyqtSignal()
    show_task_mgr_signal = pyqtSignal()
    add_task_signal = pyqtSignal(str, str) # title, deadline
    delete_task_signal = pyqtSignal(str) # task_id
    complete_task_signal = pyqtSignal(str) # task_id
    filter_tasks_signal = pyqtSignal(str) # date
    load_all_tasks_signal = pyqtSignal()
    chat_session_selected_signal = pyqtSignal(str) # session_id

    def __init__(self, user_name="User", user_role="UNKNOWN"):
        super().__init__()
        self.user_name = user_name
        self.user_role = user_role
        
        self.setWindowTitle("Ollama Vision")
        self.resize(1100, 800)
        self.setStyleSheet(STYLE_SHEET)
        
        self.selected_image_path = None
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # --- SIDEBAR (Kiri) ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(260)
        self.s_layout = QVBoxLayout(self.sidebar)
        self.s_layout.setContentsMargins(16, 24, 16, 24)
        self.s_layout.setSpacing(8)

        # Toggle Button
        self.btn_toggle = QPushButton("≡")
        self.btn_toggle.setObjectName("IconButton")
        self.btn_toggle.setFixedSize(40, 40)
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_sidebar_internal)
        self.s_layout.addWidget(self.btn_toggle)
        
        self.s_layout.addSpacing(15)

        # New Chat Button
        self.btn_new_chat = QPushButton("  ✎   New chat")
        self.btn_new_chat.setObjectName("NewChatBtn")
        self.btn_new_chat.setFixedSize(140, 40)
        self.btn_new_chat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_chat.clicked.connect(lambda: self.new_chat_signal.emit())
        self.s_layout.addWidget(self.btn_new_chat)
        
        self.s_layout.addSpacing(20)

        # Quick Find & Folders
        self.lbl_quick_find = QLabel("<b style='color:#71717a; font-size: 11px; letter-spacing: 1px;'>QUICK FIND</b>")
        self.s_layout.addWidget(self.lbl_quick_find)
        
        self.btn_task_mgr = QPushButton(" 📦   Task Manager")
        self.btn_task_mgr.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_task_mgr.clicked.connect(lambda: self.show_task_mgr_signal.emit())
        self.s_layout.addWidget(self.btn_task_mgr)
        
        self.s_layout.addSpacing(20)
        self.lbl_folder = QLabel("<b style='color:#71717a; font-size: 11px; letter-spacing: 1px;'>FOLDER</b>")
        self.s_layout.addWidget(self.lbl_folder)
        
        # Scroll Area History
        self.hist_scroll = QScrollArea()
        self.hist_scroll.setWidgetResizable(True)
        self.hist_scroll.setStyleSheet("background-color: transparent; border: none;")
        
        hist_container = QWidget()
        self.chat_layout = QVBoxLayout(hist_container)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_layout.setSpacing(2)
        self.chat_layout.addStretch()
        
        self.hist_scroll.setWidget(hist_container)
        self.s_layout.addWidget(self.hist_scroll)
        
        # Bottom Section
        self.s_layout.addStretch()
        self.btn_settings = QPushButton(" ⚙    Settings")
        self.s_layout.addWidget(self.btn_settings)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #2d2d35;")
        self.s_layout.addWidget(line)
        
        self.setup_profile_footer()
        layout.addWidget(self.sidebar)

        # --- MAIN CHAT AREA ---
        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        self.setup_header(c_layout)
        
        # Stacked Widget (Welcome, Chat, Task Manager)
        self.chat_stack = QStackedWidget()
        self.setup_welcome_screen()
        self.setup_chat_screen()
        self.setup_task_manager_screen()
        
        self.chat_stack.addWidget(self.welcome_widget)
        self.chat_stack.addWidget(self.chat_display_container)
        self.chat_stack.addWidget(self.task_manager_widget)
        c_layout.addWidget(self.chat_stack)

        # Image Preview & Input
        self.setup_input_area(c_layout)
        layout.addWidget(content)

    def setup_profile_footer(self):
        self.profile_widget = QWidget()
        p_layout = QHBoxLayout(self.profile_widget)
        p_layout.setContentsMargins(0, 16, 0, 0)
        
        lbl_avatar = QLabel("👩🏽")
        lbl_avatar.setObjectName("AIAvatar")
        lbl_avatar.setFixedSize(30, 30)
        lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.profile_info = QWidget()
        pi_inner = QVBoxLayout(self.profile_info)
        pi_inner.setSpacing(0)
        pi_inner.setContentsMargins(5, 0, 0, 0)
        lbl_name = QLabel(f"<b style='color: white; font-size: 12px;'>{self.user_name}</b>")
        lbl_role = QLabel(f"<span style='color: #71717a; font-size: 9px;'>{self.user_role}</span>")
        pi_inner.addWidget(lbl_name)
        pi_inner.addWidget(lbl_role)
        
        p_layout.addWidget(lbl_avatar)
        p_layout.addWidget(self.profile_info)
        p_layout.addStretch()
        self.s_layout.addWidget(self.profile_widget)

    def setup_header(self, layout):
        header_chat = QFrame()
        header_chat.setObjectName("HeaderChat")
        hc_layout = QHBoxLayout(header_chat)
        hc_layout.setContentsMargins(20, 15, 20, 15)
        
        self.lbl_header_title = QLabel("<b style='color: #ececee; font-size: 20px;'>Ollama Vision</b>")
        hc_layout.addWidget(self.lbl_header_title)
        hc_layout.addStretch()
        hc_layout.addWidget(QLabel("<span style='color: #9494b8; font-size: 13px;'>Model:</span>"))
        
        self.model_box = QComboBox()
        self.model_box.setObjectName("ModelSelect")
        self.model_box.setMinimumWidth(150)
        self.model_box.addItems(get_models())
        hc_layout.addWidget(self.model_box)
        layout.addWidget(header_chat)

    def setup_welcome_screen(self):
        self.welcome_widget = QWidget()
        w_layout = QVBoxLayout(self.welcome_widget)
        w_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        greeting = QLabel(f"<h1 style='color: white; font-size: 32px; font-weight: bold; margin-bottom: 5px;'>Good to see you, {self.user_name}.</h1>")
        greeting.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel("<p style='color: #9494b8; font-size: 16px; margin-top: 0px;'>Ollama AI your personal assistant for automated testing and tasks.</p>")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        def create_card(icon, title, desc):
            frame = QFrame()
            frame.setFixedSize(190, 130)
            frame.setObjectName("Card")
            card_layout = QVBoxLayout(frame)
            card_layout.setContentsMargins(15, 15, 15, 15)
            card_layout.setSpacing(5)
            lbl_icon = QLabel(f"<span style='font-size: 20px;'>{icon}</span>")
            lbl_title = QLabel(f"<b style='color: white; font-size: 14px;'>{title}</b>")
            lbl_desc = QLabel(f"<span style='color: #9494b8; font-size: 12px;'>{desc}</span>")
            lbl_desc.setWordWrap(True)
            card_layout.addWidget(lbl_icon)
            card_layout.addWidget(lbl_title)
            card_layout.addWidget(lbl_desc)
            card_layout.addStretch()
            frame.mousePressEvent = lambda event, t=title: self.input_field.setText(f"Can you help me with {t}?")
            return frame
            
        cards_layout.addWidget(create_card("📝", "Test Cases", "Generate test scenarios."))
        cards_layout.addWidget(create_card("🤖", "Automation", "Selenium/Cypress scripts."))
        cards_layout.addWidget(create_card("🐛", "Debugging", "Analyze logs & API errors."))
        cards_layout.addWidget(create_card("📚", "Docs", "Generate QA documentation."))
        
        cards_container = QWidget()
        cards_container.setLayout(cards_layout)
        
        w_layout.addStretch()
        w_layout.addWidget(greeting)
        w_layout.addWidget(subtitle)
        w_layout.addSpacing(30)
        w_layout.addWidget(cards_container, alignment=Qt.AlignmentFlag.AlignCenter)
        w_layout.addStretch()

    def setup_chat_screen(self):
        self.chat_display_container = QWidget()
        cdc_layout = QVBoxLayout(self.chat_display_container)
        cdc_layout.setContentsMargins(0, 0, 0, 0)
        cdc_layout.setSpacing(0)
        
        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setObjectName("ChatDisplay")
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.chat_history_widget = QWidget()
        self.chat_history_layout = QVBoxLayout(self.chat_history_widget)
        self.chat_history_layout.setContentsMargins(20, 20, 20, 20)
        self.chat_history_layout.setSpacing(15)
        self.chat_history_layout.addStretch()
        
        self.chat_scroll_area.setWidget(self.chat_history_widget)
        cdc_layout.addWidget(self.chat_scroll_area)
        
        self.loading_anim = LoadingAnimation()
        cdc_layout.addWidget(self.loading_anim)

    def setup_task_manager_screen(self):
        self.task_manager_widget = QWidget()
        tm_main_layout = QHBoxLayout(self.task_manager_widget)
        tm_main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left Side: CRUD
        tm_left_widget = QWidget()
        tm_layout = QVBoxLayout(tm_left_widget)
        tm_layout.setContentsMargins(30, 30, 30, 30)
        tm_layout.setSpacing(15)
        
        tm_header = QLabel("<h1 style='color: white; font-size: 26px; margin: 0;'>Task Manager</h1>")
        tm_layout.addWidget(tm_header)
        
        tm_controls = QHBoxLayout()
        self.tm_input = QLineEdit()
        self.tm_input.setPlaceholderText("Enter new task description...")
        tm_controls.addWidget(self.tm_input)
        
        btn_add = QPushButton("Add Task")
        btn_add.setObjectName("PrimaryBtn")
        btn_add.clicked.connect(lambda: self.add_task_signal.emit(self.tm_input.text().strip(), self.calendar.selectedDate().toString("yyyy-MM-dd")))
        tm_controls.addWidget(btn_add)
        
        btn_comp = QPushButton("Mark Completed")
        btn_comp.setObjectName("SuccessBtn")
        btn_comp.clicked.connect(self.complete_task_internal)
        tm_controls.addWidget(btn_comp)
        
        btn_del = QPushButton("Delete")
        btn_del.setObjectName("DangerBtn")
        btn_del.clicked.connect(self.delete_task_internal)
        tm_controls.addWidget(btn_del)
        tm_layout.addLayout(tm_controls)
        
        self.tm_table = QTableWidget()
        self.tm_table.setColumnCount(5)
        self.tm_table.setHorizontalHeaderLabels(["ID", "Title", "Status", "Date Created", "Deadline"])
        self.tm_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tm_table.setShowGrid(False)
        tm_layout.addWidget(self.tm_table)
        tm_main_layout.addWidget(tm_left_widget, stretch=1)
        
        # Right Side: Calendar
        tm_right_sidebar = QFrame()
        tm_right_sidebar.setObjectName("RightSidebar")
        tm_right_sidebar.setFixedWidth(280)
        rs_layout = QVBoxLayout(tm_right_sidebar)
        rs_layout.setContentsMargins(15, 20, 15, 15)
        
        self.calendar = QCalendarWidget()
        self.calendar.selectionChanged.connect(lambda: self.filter_tasks_signal.emit(self.calendar.selectedDate().toString("yyyy-MM-dd")))
        rs_layout.addWidget(self.calendar)
        
        btn_all = QPushButton("Show All Tasks")
        btn_all.clicked.connect(lambda: self.load_all_tasks_signal.emit())
        rs_layout.addWidget(btn_all)
        rs_layout.addStretch()
        tm_main_layout.addWidget(tm_right_sidebar)

    def setup_input_area(self, layout):
        self.preview_container = QFrame()
        self.preview_container.setStyleSheet("background-color: #202020; border-top: 1px solid #2d2d35;")
        self.preview_container.hide()
        pv_layout = QHBoxLayout(self.preview_container)
        self.preview_img = QLabel()
        self.preview_img.setFixedSize(60, 60)
        self.preview_img.setScaledContents(True)
        btn_remove = QPushButton("✕")
        btn_remove.setFixedSize(20, 20)
        btn_remove.setStyleSheet("background-color: #ef4444; color: white; border-radius: 10px;")
        btn_remove.clicked.connect(self.clear_image)
        pv_layout.addWidget(self.preview_img)
        pv_layout.addWidget(btn_remove)
        pv_layout.addStretch()
        layout.addWidget(self.preview_container)

        self.input_container = QFrame()
        self.input_container.setObjectName("InputContainer")
        input_h = QHBoxLayout(self.input_container)
        
        btn_up = QPushButton("🖼️")
        btn_up.setObjectName("IconButton")
        btn_up.clicked.connect(self.open_image)
        input_h.addWidget(btn_up)

        self.input_field = QLineEdit()
        self.input_field.setObjectName("InputBox")
        self.input_field.setPlaceholderText("Ask or search anything...")
        self.input_field.returnPressed.connect(self.emit_send_signal)
        input_h.addWidget(self.input_field)
        
        btn_send = QPushButton("🚀")
        btn_send.setObjectName("PrimaryBtn")
        btn_send.setFixedSize(44, 44)
        btn_send.clicked.connect(self.emit_send_signal)
        input_h.addWidget(btn_send)
        layout.addWidget(self.input_container)

    def toggle_sidebar_internal(self):
        is_collapsed = self.sidebar.width() < 100
        if not is_collapsed:
            self.sidebar.setFixedWidth(80)
            self.btn_new_chat.setText("  ✎")
            self.btn_new_chat.setFixedWidth(40)
            for w in [self.lbl_quick_find, self.btn_task_mgr, self.lbl_folder, self.hist_scroll, self.btn_settings, self.profile_info]:
                w.hide()
        else:
            self.sidebar.setFixedWidth(260)
            self.btn_new_chat.setText("  ✎   New chat")
            self.btn_new_chat.setFixedWidth(140)
            for w in [self.lbl_quick_find, self.btn_task_mgr, self.lbl_folder, self.hist_scroll, self.btn_settings, self.profile_info]:
                w.show()

    def open_image(self):
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if path:
            self.selected_image_path = path
            pixmap = QPixmap(path)
            self.preview_img.setPixmap(pixmap)
            self.preview_container.show()

    def clear_image(self):
        self.selected_image_path = None
        self.preview_container.hide()

    def emit_send_signal(self):
        text = self.input_field.text().strip()
        img = self.selected_image_path
        if text or img:
            self.send_message_signal.emit(text, img)
            self.input_field.clear()
            self.clear_image()

    def complete_task_internal(self):
        row = self.tm_table.currentRow()
        if row >= 0:
            tid = self.tm_table.item(row, 0).text()
            self.complete_task_signal.emit(tid)

    def delete_task_internal(self):
        row = self.tm_table.currentRow()
        if row >= 0:
            tid = self.tm_table.item(row, 0).text()
            self.delete_task_signal.emit(tid)

    def add_sidebar_button(self, session_id, name):
        btn = QPushButton()
        btn_layout = QVBoxLayout(btn)
        top_layout = QHBoxLayout()
        lbl_title = QLabel(f"<b style='color: #e1e1e6; font-size: 13px;'>{name}</b>")
        top_layout.addWidget(lbl_title)
        top_layout.addStretch()
        top_layout.addWidget(QLabel("<span style='color: #52525b; font-size: 12px;'>📌</span>"))
        btn_layout.addLayout(top_layout)
        btn_layout.addWidget(QLabel("<span style='color: #71717a; font-size: 11px;'>Chat session...</span>"))
        btn.setFixedHeight(55)
        btn.setObjectName("NewChatBtn")
        btn.clicked.connect(lambda: self.chat_session_selected_signal.emit(session_id))
        self.chat_layout.insertWidget(0, btn)

    def create_chat_bubble(self, is_user, html_text, image_path=None):
        container = QWidget()
        layout = QHBoxLayout(container)
        bubble_frame = QFrame()
        bubble_layout = QVBoxLayout(bubble_frame)
        
        if image_path:
            img_lbl = QLabel()
            img_lbl.setPixmap(QPixmap(image_path).scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio))
            bubble_layout.addWidget(img_lbl)

        bubble_label = QLabel(html_text)
        bubble_label.setWordWrap(True)
        bubble_label.setMaximumWidth(600)
        bubble_layout.addWidget(bubble_label)
        
        avatar = QLabel("👱🏻‍♀️" if is_user else "✨")
        avatar.setObjectName("UserAvatar" if is_user else "AIAvatar")
        avatar.setFixedSize(36, 36)
        
        if is_user:
            bubble_frame.setObjectName("UserBubble")
            layout.addStretch()
            layout.addWidget(bubble_frame)
            layout.addWidget(avatar)
        else:
            bubble_frame.setObjectName("AIBubble")
            layout.addWidget(avatar)
            layout.addWidget(bubble_frame)
            layout.addStretch()
        return container
