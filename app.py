import sys
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextBrowser, QLineEdit, QPushButton, 
                             QComboBox, QLabel, QFrame, QScrollArea, QSpacerItem, 
                             QSizePolicy, QStackedWidget, QDialog, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QCalendarWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QTextCursor, QColor, QPixmap, QIcon
from langchain_ollama import OllamaLLM
import mysql.connector
from mysql.connector import errorcode
import os

from style import STYLE_SHEET, COLOR_ACCENT

class ChatWorker(QThread):
    response_ready = pyqtSignal(str)
    
    def __init__(self, model, context, images=None):
        super().__init__()
        self.model = model
        self.context = context
        self.images = images
        
    def run(self):
        try:
            llm = OllamaLLM(model=self.model)
            if self.images:
                # Note: OllamaLLM from langchain_ollama supports 'images' in bind or invoke
                # However, raw invoke might need specific formatting for vision
                response = llm.invoke(self.context, images=self.images)
            else:
                response = llm.invoke(self.context)
            self.response_ready.emit(response)
        except Exception as e:
            self.response_ready.emit(f"Error: {str(e)}")

class LoadingAnimation(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("Bot is typing...")
        self.setStyleSheet("color: #a855f7; font-style: italic; font-size: 13px; margin-left: 55px; margin-top: 5px; margin-bottom: 5px;")
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
        self.input_name.setStyleSheet("""
            QLineEdit { background-color: #25252b; border: 1px solid #3f3f46; border-radius: 10px; padding: 15px; font-size: 16px; color: white; }
        """)
        layout.addWidget(QLabel("<b style='color:#e1e1e6; font-size: 16px;'>Name:</b>"))
        layout.addWidget(self.input_name)
        
        # Role Input
        self.input_role = QLineEdit()
        self.input_role.setPlaceholderText("Enter your role/profession...")
        self.input_role.setStyleSheet("""
            QLineEdit { background-color: #25252b; border: 1px solid #3f3f46; border-radius: 10px; padding: 15px; font-size: 16px; color: white; }
        """)
        layout.addWidget(QLabel("<b style='color:#e1e1e6; font-size: 16px;'>Role:</b>"))
        layout.addWidget(self.input_role)
        
        # Start Button
        btn_start = QPushButton("Start Chatting")
        btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_start.setStyleSheet("""
            QPushButton {
                background-color: #a855f7;
                color: white;
                border-radius: 12px;
                padding: 15px;
                font-weight: bold;
                font-size: 16px;
            }
        """)
        btn_start.clicked.connect(self.accept_data)
        layout.addWidget(btn_start)
        layout.addStretch()

    def accept_data(self):
        name = self.input_name.text().strip()
        role = self.input_role.text().strip()
        if name: self.user_name = name
        if role: self.user_role = role.upper()
        self.accept()

class OllamaAIApp(QMainWindow):
    def __init__(self, user_name="User", user_role="UNKNOWN"):
        super().__init__()
        self.user_name = user_name
        self.user_role = user_role
        
        print("Starting OllamaAIApp.__init__")
        self.setWindowTitle("Ollama Vision")
        self.resize(1100, 800)
        print("Setting style sheet")
        self.setStyleSheet(STYLE_SHEET)
        self.chat_sessions = {}
        self.current_session_id = None
        self.session_counter = 0
        self.selected_image_path = None
        
        print("Initializing Database")
        self.init_db()
        print("Initializing UI")
        self.init_ui()
        print("OllamaAIApp initialized")

    def init_db(self):
        print("DEBUG: Entering init_db")
        try:
            print("DEBUG: Attempting to connect to MySQL (pure Python mode)...")
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="ollama_assistant",
                use_pure=True,  # Menggunakan implementasi Python murni untuk menghindari crash DLL
                connection_timeout=5 # Timeout agar tidak gantung
            )
            print("DEBUG: Connected successfully to existing database.")
        except mysql.connector.Error as err:
            print(f"DEBUG: MySQL Error caught: {err.errno} - {err}")
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                print("DEBUG: Database not found, attempting to create...")
                try:
                    # Juga gunakan use_pure di sini!
                    temp_db = mysql.connector.connect(
                        host="localhost", 
                        user="root", 
                        password="",
                        use_pure=True,
                        connection_timeout=5
                    )
                    cursor = temp_db.cursor()
                    cursor.execute("CREATE DATABASE ollama_assistant")
                    temp_db.close()
                    print("DEBUG: Database created successfully, reconnecting...")
                    self.db = mysql.connector.connect(
                        host="localhost", 
                        user="root", 
                        password="", 
                        database="ollama_assistant",
                        use_pure=True,
                        connection_timeout=5
                    )
                except Exception as e:
                    print(f"DEBUG: Crash during DB creation: {e}")
                    self.db = None
                    return
            else:
                print(f"Error Database: {err}")
                self.db = None
                return
        except Exception as e:
            print(f"DEBUG: Unexpected crash in init_db: {e}")
            self.db = None
            return
                
        if self.db:
            print("DEBUG: Creating tables if not exist...")
            try:
                cursor = self.db.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        status ENUM('pending', 'completed') DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        deadline DATE NULL
                    )
                """)
                self.db.commit()
                print("DEBUG: Database initialization complete.")
            except Exception as e:
                print(f"DEBUG: Error creating tables: {e}")
        else:
            print("DEBUG: self.db is None, skipping table creation.")

    def get_models(self):
        try:
            result = subprocess.run(["ollama", "list"], stdout=subprocess.PIPE, text=True)
            return [line.split()[0] for line in result.stdout.strip().split("\n")[1:]]
        except: return []

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
        self.sidebar.setStyleSheet("background-color: #1a1a1f; border-right: 1px solid #2d2d35;")
        self.s_layout = QVBoxLayout(self.sidebar)
        self.s_layout.setContentsMargins(15, 20, 15, 15)

        # 1. Top Section: Hamburger & New Chat (Vertical Gemini Style)
        self.btn_toggle = QPushButton("≡")
        self.btn_toggle.setFixedSize(40, 40)
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.setStyleSheet("""
            QPushButton { font-size: 24px; color: #9494b8; background: transparent; border: none; }
            QPushButton:hover { background-color: #2d2d35; border-radius: 20px; }
        """)
        self.btn_toggle.clicked.connect(self.toggle_sidebar)
        self.s_layout.addWidget(self.btn_toggle)
        
        self.s_layout.addSpacing(15)

        # New Chat Button (Pill Style)
        self.btn_new_chat = QPushButton("  ✎   New chat")
        self.btn_new_chat.setFixedSize(140, 40)
        self.btn_new_chat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_chat.setStyleSheet("""
            QPushButton {
                text-align: left;
                background-color: transparent;
                color: #e1e1e6;
                border-radius: 20px;
                padding-left: 5px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2d2d35;
            }
        """)
        self.btn_new_chat.clicked.connect(self.reset_chat)
        self.s_layout.addWidget(self.btn_new_chat)
        
        self.s_layout.addSpacing(20)

        # 2. Quick Find & Folders
        self.lbl_quick_find = QLabel("<b style='color:#71717a; font-size: 11px; letter-spacing: 1px;'>QUICK FIND</b>")
        self.s_layout.addWidget(self.lbl_quick_find)
        
        self.btn_task_mgr = QPushButton(" 📦   Task Manager")
        self.btn_task_mgr.setStyleSheet("""
            QPushButton { text-align: left; background-color: transparent; color: #e1e1e6; padding: 10px; border-radius: 8px; font-size: 13px; font-weight: bold; }
            QPushButton:hover { background-color: #25252b; }
        """)
        self.btn_task_mgr.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_task_mgr.clicked.connect(self.show_task_manager)
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
        
        # 4. Bottom Section: Settings & Profile
        self.s_layout.addStretch()
        
        self.btn_settings = QPushButton(" ⚙    Settings")
        self.btn_settings.setStyleSheet("""
            QPushButton { text-align: left; background-color: transparent; color: #71717a; padding: 10px; border-radius: 8px; font-size: 13px; }
            QPushButton:hover { background-color: #25252b; color: white; }
        """)
        self.s_layout.addWidget(self.btn_settings)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #2d2d35;")
        self.s_layout.addWidget(line)
        
        self.profile_widget = QWidget()
        p_layout = QHBoxLayout(self.profile_widget)
        p_layout.setContentsMargins(0, 10, 0, 0)
        
        lbl_avatar = QLabel("👩🏽")
        lbl_avatar.setStyleSheet("font-size: 20px; background: #3f3f46; border-radius: 15px; padding: 2px;")
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

        layout.addWidget(self.sidebar)

        # --- MAIN CHAT AREA (Kanan) ---
        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header Chat (Model Selector)
        header_chat = QFrame()
        header_chat.setStyleSheet("background-color: #1a1a1f; border-bottom: 1px solid #2d2d35;")
        hc_layout = QHBoxLayout(header_chat)
        hc_layout.setContentsMargins(20, 15, 20, 15)
        
        self.lbl_header_title = QLabel("<b style='color: #ececee; font-size: 20px;'>Ollama Vision</b>")
        hc_layout.addWidget(self.lbl_header_title)
        hc_layout.addStretch()
        hc_layout.addWidget(QLabel("<span style='color: #9494b8; font-size: 13px;'>Model:</span>"))
        
        self.model_box = QComboBox()
        self.model_box.setObjectName("ModelSelect")
        self.model_box.setMinimumWidth(150)
        self.model_box.addItems(self.get_models())
        hc_layout.addWidget(self.model_box)
        
        c_layout.addWidget(header_chat)

        self.chat_stack = QStackedWidget()
        
        # 1. Welcome Screen
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
            frame.setStyleSheet("""
                QFrame {
                    background-color: #1c1c21;
                    border: 1px solid #2d2d35;
                    border-radius: 12px;
                }
                QFrame:hover {
                    background-color: #25252b;
                    border: 1px solid #5b21b6;
                }
            """)
            card_layout = QVBoxLayout(frame)
            card_layout.setContentsMargins(15, 15, 15, 15)
            card_layout.setSpacing(5)
            
            lbl_icon = QLabel(f"<span style='font-size: 20px;'>{icon}</span>")
            lbl_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            lbl_title = QLabel(f"<b style='color: white; font-size: 14px;'>{title}</b>")
            lbl_title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            lbl_desc = QLabel(f"<span style='color: #9494b8; font-size: 12px;'>{desc}</span>")
            lbl_desc.setWordWrap(True)
            lbl_desc.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            
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
        
        # 2. Chat Display Screen
        self.chat_display_container = QWidget()
        cdc_layout = QVBoxLayout(self.chat_display_container)
        cdc_layout.setContentsMargins(0, 0, 0, 0)
        cdc_layout.setSpacing(0)
        
        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setObjectName("ChatDisplay")
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; } QScrollBar:vertical { width: 10px; background: transparent; }")
        
        self.chat_history_widget = QWidget()
        self.chat_history_widget.setStyleSheet("background-color: transparent;")
        self.chat_history_layout = QVBoxLayout(self.chat_history_widget)
        self.chat_history_layout.setContentsMargins(20, 20, 20, 20)
        self.chat_history_layout.setSpacing(15)
        self.chat_history_layout.addStretch()
        
        self.chat_scroll_area.setWidget(self.chat_history_widget)
        cdc_layout.addWidget(self.chat_scroll_area)
        
        self.loading_anim = LoadingAnimation()
        cdc_layout.addWidget(self.loading_anim)
        
        self.chat_stack.addWidget(self.welcome_widget)
        self.chat_stack.addWidget(self.chat_display_container)
        
        # 3. Task Manager Screen
        self.task_manager_widget = QWidget()
        tm_main_layout = QHBoxLayout(self.task_manager_widget)
        tm_main_layout.setContentsMargins(0, 0, 0, 0)
        tm_main_layout.setSpacing(0)
        
        # --- Left Side: Task Manager CRUD ---
        tm_left_widget = QWidget()
        tm_layout = QVBoxLayout(tm_left_widget)
        tm_layout.setContentsMargins(30, 30, 30, 30)
        tm_layout.setSpacing(15)
        
        tm_header = QLabel("<h1 style='color: white; font-size: 26px; margin: 0;'>Task Manager</h1>")
        tm_desc = QLabel("<p style='color: #9494b8; font-size: 14px;'>Manage your tasks and projects in one place.</p>")
        tm_layout.addWidget(tm_header)
        tm_layout.addWidget(tm_desc)
        
        # Top controls
        tm_controls = QHBoxLayout()
        self.tm_input = QLineEdit()
        self.tm_input.setPlaceholderText("Enter new task description...")
        self.tm_input.setStyleSheet("background-color: #25252b; border: 1px solid #3f3f46; border-radius: 8px; padding: 12px; color: white; font-size: 14px;")
        tm_controls.addWidget(self.tm_input)
        
        btn_tm_add = QPushButton("Add Task")
        btn_tm_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_tm_add.setStyleSheet("background-color: #a855f7; color: white; border-radius: 8px; padding: 12px 20px; font-weight: bold;")
        btn_tm_add.clicked.connect(self.tm_add_task)
        tm_controls.addWidget(btn_tm_add)
        
        btn_tm_complete = QPushButton("Mark Completed")
        btn_tm_complete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_tm_complete.setStyleSheet("background-color: #10b981; color: white; border-radius: 8px; padding: 12px 20px; font-weight: bold;")
        btn_tm_complete.clicked.connect(self.tm_complete_task)
        tm_controls.addWidget(btn_tm_complete)
        
        btn_tm_del = QPushButton("Delete Selected")
        btn_tm_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_tm_del.setStyleSheet("background-color: #ef4444; color: white; border-radius: 8px; padding: 12px 20px; font-weight: bold;")
        btn_tm_del.clicked.connect(self.tm_delete_task)
        tm_controls.addWidget(btn_tm_del)
        
        tm_layout.addLayout(tm_controls)
        
        # Table
        self.tm_table = QTableWidget()
        self.tm_table.setColumnCount(5)
        self.tm_table.setHorizontalHeaderLabels(["ID", "Title", "Status", "Date Created", "Deadline"])
        self.tm_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tm_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tm_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tm_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tm_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.tm_table.setStyleSheet("""
            QTableWidget { background-color: #1c1c21; color: white; border: 1px solid #2d2d35; border-radius: 8px; gridline-color: #2d2d35; }
            QHeaderView::section { background-color: #25252b; color: #9494b8; padding: 10px; border: none; font-weight: bold; text-align: left; }
            QTableView::item { border-bottom: 1px solid #2d2d35; padding: 5px; }
        """)
        self.tm_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tm_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tm_table.verticalHeader().setVisible(False)
        self.tm_table.setShowGrid(False)
        tm_layout.addWidget(self.tm_table)
        
        tm_main_layout.addWidget(tm_left_widget, stretch=1)
        
        # --- Right Side: Calendar Dashboard ---
        tm_right_sidebar = QFrame()
        tm_right_sidebar.setObjectName("RightSidebar")
        tm_right_sidebar.setFixedWidth(280)
        tm_right_sidebar.setStyleSheet("background-color: #1a1a1f; border-left: 1px solid #2d2d35;")
        rs_layout = QVBoxLayout(tm_right_sidebar)
        rs_layout.setContentsMargins(15, 20, 15, 15)
        
        lbl_cal = QLabel("<h3 style='color: white; margin: 0;'>Academic Calendar</h3>")
        rs_layout.addWidget(lbl_cal)
        
        lbl_hint = QLabel("<span style='color: #71717a; font-size: 11px;'>Select a date to set a deadline for a new task, or filter existing tasks by deadline.</span>")
        lbl_hint.setWordWrap(True)
        rs_layout.addWidget(lbl_hint)
        rs_layout.addSpacing(10)
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setStyleSheet("""
            QCalendarWidget QWidget { alternate-background-color: #25252b; }
            QCalendarWidget QToolButton { color: white; background-color: transparent; }
            QCalendarWidget QMenu { background-color: #25252b; color: white; }
            QCalendarWidget QSpinBox { background-color: #25252b; color: white; }
            QCalendarWidget QAbstractItemView:enabled { background-color: #1c1c21; color: white; selection-background-color: #a855f7; selection-color: white; }
            QCalendarWidget QAbstractItemView:disabled { color: #52525b; }
        """)
        self.calendar.selectionChanged.connect(self.filter_tasks_by_date)
        rs_layout.addWidget(self.calendar)
        
        btn_show_all = QPushButton("Show All Tasks")
        btn_show_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_show_all.setStyleSheet("background-color: #3f3f46; color: white; border-radius: 8px; padding: 10px; margin-top: 10px; font-weight: bold;")
        btn_show_all.clicked.connect(self.tm_load_data)
        rs_layout.addWidget(btn_show_all)
        
        rs_layout.addStretch()
        
        tm_main_layout.addWidget(tm_right_sidebar)
        
        self.chat_stack.addWidget(self.task_manager_widget)
        
        c_layout.addWidget(self.chat_stack)

        # 1. Image Preview (Hidden by default)
        self.preview_container = QFrame()
        self.preview_container.setStyleSheet("background-color: #202020; border-top: 1px solid #2d2d35;")
        self.preview_container.hide()
        pv_layout = QHBoxLayout(self.preview_container)
        pv_layout.setContentsMargins(20, 10, 20, 10)
        
        self.preview_img = QLabel()
        self.preview_img.setFixedSize(60, 60)
        self.preview_img.setStyleSheet("border-radius: 8px; background-color: #111;")
        self.preview_img.setScaledContents(True)
        
        btn_remove_img = QPushButton("✕")
        btn_remove_img.setFixedSize(20, 20)
        btn_remove_img.setStyleSheet("background-color: #ef4444; color: white; border-radius: 10px; font-weight: bold;")
        btn_remove_img.clicked.connect(self.clear_image)
        
        pv_layout.addWidget(self.preview_img)
        pv_layout.addWidget(btn_remove_img)
        pv_layout.addStretch()
        
        c_layout.addWidget(self.preview_container)

        # 2. Input Field ala gambar
        input_container = QFrame()
        input_container.setObjectName("InputContainer")
        input_h = QHBoxLayout(input_container)
        
        # Upload Image Button
        self.btn_upload = QPushButton("🖼️")
        self.btn_upload.setFixedSize(40, 40)
        self.btn_upload.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_upload.setStyleSheet("font-size: 18px; color: #9494b8; background: transparent; border: none;")
        self.btn_upload.clicked.connect(self.open_image)
        input_h.addWidget(self.btn_upload)

        self.input_field = QLineEdit()
        self.input_field.setObjectName("InputBox")
        self.input_field.setPlaceholderText("Ask or search anything...")
        self.input_field.returnPressed.connect(self.handle_send)
        
        send_btn = QPushButton("🚀")
        send_btn.setFixedSize(40, 40)
        send_btn.setStyleSheet(f"background-color: {COLOR_ACCENT}; border-radius: 20px; color: white;")
        send_btn.clicked.connect(self.handle_send)

        input_h.addWidget(self.input_field)
        input_h.addWidget(send_btn)
        
        c_layout.addWidget(input_container)
        layout.addWidget(content)

    def toggle_sidebar(self):
        if self.sidebar.width() > 100:
            # Collapse
            self.sidebar.setFixedWidth(80)
            self.btn_new_chat.setText("  ✎")
            self.btn_new_chat.setFixedWidth(40)
            
            self.lbl_quick_find.hide()
            self.btn_task_mgr.hide()
            self.lbl_folder.hide()
            self.hist_scroll.hide()
            self.btn_settings.hide()
            self.profile_info.hide()
        else:
            # Expand
            self.sidebar.setFixedWidth(260)
            self.btn_new_chat.setText("  ✎   New chat")
            self.btn_new_chat.setFixedWidth(140)
            
            self.lbl_quick_find.show()
            self.btn_task_mgr.show()
            self.lbl_folder.show()
            self.hist_scroll.show()
            self.btn_settings.show()
            self.profile_info.show()

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

    def show_task_manager(self):
        self.chat_stack.setCurrentIndex(2)
        # Hide the chat input box when in task manager
        input_container = self.findChild(QFrame, "InputContainer")
        if input_container:
            input_container.hide()
        self.tm_load_data()

    def check_db_schema(self):
        # Memastikan kolom deadline ada di database (untuk menangani update retroaktif db)
        if not self.db: return
        cursor = self.db.cursor()
        try:
            cursor.execute("SHOW COLUMNS FROM tasks LIKE 'deadline'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE tasks ADD COLUMN deadline DATE NULL")
            self.db.commit()
        except: pass

    def tm_load_data(self, filter_date=None):
        self.check_db_schema()
        if not self.db: return
        cursor = self.db.cursor(dictionary=True)
        
        if filter_date:
            cursor.execute("SELECT * FROM tasks WHERE deadline = %s ORDER BY created_at DESC", (filter_date,))
        else:
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
             
        tasks = cursor.fetchall()
        
        self.tm_table.setRowCount(0)
        for i, task in enumerate(tasks):
            self.tm_table.insertRow(i)
            self.tm_table.setItem(i, 0, QTableWidgetItem(str(task['id'])))
            self.tm_table.setItem(i, 1, QTableWidgetItem(task['title']))
            
            # Status badge styling
            status_item = QTableWidgetItem(task['status'].upper())
            status_item.setForeground(QColor("#10b981") if task['status'] == 'completed' else QColor("#f59e0b"))
            self.tm_table.setItem(i, 2, status_item)
            
            self.tm_table.setItem(i, 3, QTableWidgetItem(str(task['created_at'].strftime("%Y-%m-%d %H:%M"))))
            
            deadline_str = str(task['deadline']) if task['deadline'] else "No Deadline"
            self.tm_table.setItem(i, 4, QTableWidgetItem(deadline_str))

    def filter_tasks_by_date(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.tm_load_data(filter_date=selected_date)

    def tm_add_task(self):
        title = self.tm_input.text().strip()
        if not title: return
        
        if not self.db:
            QMessageBox.warning(self, "Database Error", "Cannot add task: Not connected to MySQL. Please make sure XAMPP / MySQL server is running on localhost with user 'root' and empty password.")
            return
            
        # ambil tanggal dari kalendar untuk input
        deadline = self.calendar.selectedDate().toString("yyyy-MM-dd")
        
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO tasks (title, deadline) VALUES (%s, %s)", (title, deadline))
        self.db.commit()
        self.tm_input.clear()
        self.tm_load_data()

    def tm_delete_task(self):
        current_row = self.tm_table.currentRow()
        if current_row < 0 or not self.db: return
        task_id = self.tm_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(self, 'Delete Task', 'Are you sure you want to delete this task?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            self.db.commit()
            self.tm_load_data()

    def tm_complete_task(self):
        current_row = self.tm_table.currentRow()
        if current_row < 0 or not self.db: return
        task_id = self.tm_table.item(current_row, 0).text()
        
        cursor = self.db.cursor()
        cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = %s", (task_id,))
        self.db.commit()
        self.tm_load_data()
        self.load_tasks()

    def delete_task(self, task_id):
        if not self.db: return
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        self.db.commit()

    def add_sidebar_button(self, session_id, name):
        # Format sesuai referensi gambar (Title tebal, deskripsi kecil, pin icon)
        btn = QPushButton()
        btn_layout = QVBoxLayout(btn)
        btn_layout.setContentsMargins(10, 8, 10, 8)
        btn_layout.setSpacing(2)
        
        # Header (Nama Chat & Ikon)
        top_layout = QHBoxLayout()
        lbl_title = QLabel(f"<b style='color: #e1e1e6; font-size: 13px;'>{name}</b>")
        lbl_title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        top_layout.addWidget(lbl_title)
        top_layout.addStretch()
        # Simulated Pin Icon as requested by the style
        lbl_pin = QLabel("<span style='color: #52525b; font-size: 12px;'>📌</span>")
        top_layout.addWidget(lbl_pin)
        
        # Subtitle
        lbl_desc = QLabel("<span style='color: #71717a; font-size: 11px;'>Chat session details...</span>")
        lbl_desc.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        btn_layout.addLayout(top_layout)
        btn_layout.addWidget(lbl_desc)
        
        btn.setStyleSheet("""
            QPushButton {
                text-align: left; 
                background-color: transparent;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #25252b;
            }
        """)
        btn.setFixedHeight(55)
        btn.clicked.connect(lambda checked, sid=session_id: self.load_chat(sid))
        self.chat_layout.insertWidget(0, btn)

    def create_chat_bubble(self, is_user, html_text):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        bubble_frame = QFrame()
        bubble_layout = QVBoxLayout(bubble_frame)
        bubble_layout.setContentsMargins(15, 12, 15, 12)
        
        bubble_label = QLabel(html_text)
        bubble_label.setWordWrap(True)
        bubble_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        bubble_label.setMaximumWidth(600)
        
        bubble_layout.addWidget(bubble_label)
        
        # Check if there is an image in this message (Custom logic for our app)
        # We'll pass an optional 'image_path' to create_chat_bubble if needed
        
        if is_user:
            bubble_frame.setStyleSheet("""
                QFrame {
                    background-color: #b538b0;
                    border-radius: 18px;
                }
                QLabel {
                    color: #ffffff;
                    font-size: 14px;
                    line-height: 1.4;
                    background-color: transparent;
                }
            """)
            
            avatar = QLabel("👱🏻‍♀️")
            avatar.setStyleSheet("font-size: 24px; background-color: transparent;")
            avatar.setFixedSize(36, 36)
            avatar.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            
            layout.addStretch()
            layout.addWidget(bubble_frame)
            layout.addWidget(avatar)
            layout.setAlignment(bubble_frame, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
            layout.setAlignment(avatar, Qt.AlignmentFlag.AlignTop)
        else:
            bubble_frame.setStyleSheet("""
                QFrame {
                    background-color: #202020;
                    border-radius: 18px;
                }
                QLabel {
                    color: #e1e1e6;
                    font-size: 14px;
                    line-height: 1.4;
                    background-color: transparent;
                }
            """)
            
            avatar = QLabel("✨")
            avatar.setStyleSheet("font-size: 20px; background-color: #111; border-radius: 12px; padding: 5px;")
            avatar.setFixedSize(36, 36)
            avatar.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            
            layout.addWidget(avatar)
            layout.addWidget(bubble_frame)
            layout.addStretch()
            layout.setAlignment(bubble_frame, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            layout.setAlignment(avatar, Qt.AlignmentFlag.AlignTop)
            
        return container

    def append_message(self, sender, text, save=True, image_path=None):
        is_user = sender == "You"
        formatted_text = text.replace('\n', '<br>')
        
        bubble_container = self.create_chat_bubble(is_user, formatted_text)
        
        # If image, add it above the text label in the bubble
        if image_path:
            # Find the bubble frame's layout
            frame = bubble_container.findChild(QFrame)
            if frame:
                flayout = frame.layout()
                img_lbl = QLabel()
                img_lbl.setPixmap(QPixmap(image_path).scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                img_lbl.setStyleSheet("border-radius: 10px; margin-bottom: 10px;")
                flayout.insertWidget(0, img_lbl)

        if save:
            if self.current_session_id is None:
                self.session_counter += 1
                self.current_session_id = f"session_{self.session_counter}"
                name = text[:20] + "..." if len(text) > 20 else text
                self.chat_sessions[self.current_session_id] = {
                    "name": name,
                    "history": [],
                    "llm_history": []
                }
                self.add_sidebar_button(self.current_session_id, name)
            
            self.chat_sessions[self.current_session_id]["history"].append((sender, text))
            msg_str = f"{sender}: {text}"
            if image_path: msg_str += " [Image Attached]"
            self.chat_sessions[self.current_session_id]["llm_history"].append(msg_str)

        self.chat_history_layout.insertWidget(self.chat_history_layout.count() - 1, bubble_container)

        QApplication.processEvents()
        scrollbar = self.chat_scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def handle_send(self):
        text = self.input_field.text().strip()
        img_path = self.selected_image_path
        if not text and not img_path: return
        
        self.chat_stack.setCurrentIndex(1)
        input_c = self.findChild(QFrame, "InputContainer")
        if input_c: input_c.show()
        
        self.append_message("You", text, save=True, image_path=img_path)
        self.input_field.clear()
        self.clear_image() # Reset image preview
        
        context = "\n".join(self.chat_sessions[self.current_session_id]["llm_history"][-10:])
        
        # Prepare images for worker
        base64_images = []
        if img_path:
            with open(img_path, "rb") as image_file:
                base64_images.append(base64.b64encode(image_file.read()).decode('utf-8'))
        
        self.loading_anim.show()
        
        self.worker = ChatWorker(self.model_box.currentText(), context, images=base64_images if base64_images else None)
        self.worker.response_ready.connect(self.handle_response)
        self.worker.start()

    def handle_response(self, response):
        self.loading_anim.hide()
        self.append_message("Ollama AI", response, save=True)

    def clear_chat_history(self):
        while self.chat_history_layout.count() > 1:
            item = self.chat_history_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def reset_chat(self):
        self.clear_chat_history()
        self.current_session_id = None
        self.chat_stack.setCurrentIndex(0)
        input_c = self.findChild(QFrame, "InputContainer")
        if input_c: input_c.show()

    def load_chat(self, session_id):
        self.clear_chat_history()
        self.current_session_id = session_id
        self.chat_stack.setCurrentIndex(1)
        input_c = self.findChild(QFrame, "InputContainer")
        if input_c: input_c.show()
        
        session_data = self.chat_sessions[session_id]
        
        for sender, text in session_data["history"]:
            self.append_message(sender, text, save=False)

if __name__ == "__main__":
    print("Starting QApplication...")
    app = QApplication(sys.argv)
    
    # Menampilkan Setup Profile Dialog terlebih dahulu
    print("Opening Setup Dialog...")
    setup_dialog = ProfileSetupDialog()
    if setup_dialog.exec() == QDialog.DialogCode.Accepted or True: 
        print("Setup Dialog finished, creating main window...")
        window = OllamaAIApp(user_name=setup_dialog.user_name, user_role=setup_dialog.user_role)
        window.show()
        print("Application running...")
        sys.exit(app.exec())