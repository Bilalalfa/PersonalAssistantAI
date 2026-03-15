import sys
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextBrowser, QLineEdit, QPushButton, 
                             QComboBox, QLabel, QFrame, QScrollArea, QSpacerItem, QSizePolicy, QStackedWidget, QDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QTextCursor, QColor
from langchain_ollama import OllamaLLM
import mysql.connector
from datetime import datetime

from style import STYLE_SHEET, COLOR_ACCENT

class ChatWorker(QThread):
    response_ready = pyqtSignal(str)
    
    def __init__(self, model, context):
        super().__init__()
        self.model = model
        self.context = context
        
    def run(self):
        try:
            llm = OllamaLLM(model=self.model)
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
        self.setWindowTitle("Welcome to Ollama AI")
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
        
        self.setWindowTitle("Ollama AI")
        self.resize(1100, 800)
        self.setStyleSheet(STYLE_SHEET)
        self.chat_sessions = {}
        self.current_session_id = None
        self.session_counter = 0
        self.init_db()
        self.init_ui()

    def init_db(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",  # Sesuaikan jika MySQL lokal menggunakan password
                database="ollama_assistant"
            )
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                # Database belum ada, buat baru
                temp_db = mysql.connector.connect(host="localhost", user="root", password="")
                cursor = temp_db.cursor()
                cursor.execute("CREATE DATABASE ollama_assistant")
                temp_db.close()
                self.db = mysql.connector.connect(host="localhost", user="root", password="", database="ollama_assistant")
            else:
                print(f"Error Database: {err}")
                self.db = None
                return
                
        cursor = self.db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                status ENUM('pending', 'completed') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.commit()

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
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)
        s_layout = QVBoxLayout(sidebar)
        s_layout.setContentsMargins(15, 20, 15, 15)

        # Header Sidebar (Logo)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_robot = QLabel("🤖")
        lbl_robot.setStyleSheet("font-size: 24px; background: #2d2d35; border-radius: 8px; padding: 5px;")
        lbl_robot.setFixedSize(36, 36)
        lbl_robot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(lbl_robot)
        
        logo = QLabel("<b style='color:white; font-size: 16px; margin-left: 5px;'>Ollama AI</b>")
        header_layout.addWidget(logo)
        header_layout.addStretch()
        
        btn_collapse = QPushButton("◫")
        btn_collapse.setStyleSheet("color: #9494b8; background: #25252b; border-radius: 12px; padding: 5px 10px;")
        header_layout.addWidget(btn_collapse)
        s_layout.addLayout(header_layout)
        
        s_layout.addSpacing(20)

        # New Chat Button
        new_chat = QPushButton("＋ New Chat")
        new_chat.setStyleSheet("""
            QPushButton {
                background-color: #f3effe;
                color: #5b21b6;
                border-radius: 20px;
                padding: 12px;
                font-weight: bold;
                border: 1px solid #e9d5ff;
            }
            QPushButton:hover {
                background-color: #e9d5ff;
            }
        """)
        new_chat.clicked.connect(self.reset_chat)
        s_layout.addWidget(new_chat)
        
        s_layout.addSpacing(15)

        # Search Box
        search_box = QLineEdit()
        search_box.setPlaceholderText("🔍 Search by feature, tag...")
        search_box.setStyleSheet("""
            QLineEdit {
                background-color: #25252b;
                border: none;
                border-radius: 18px;
                padding: 10px 15px;
                color: white;
            }
        """)
        s_layout.addWidget(search_box)
        
        s_layout.addSpacing(20)
        
        # --- TASK MANAGER SECTION ---
        task_header = QHBoxLayout()
        lbl_tasks = QLabel("<b style='color:#71717a; font-size: 11px; letter-spacing: 1px;'>TASKS</b>")
        task_header.addWidget(lbl_tasks)
        task_header.addStretch()
        
        btn_add_task = QPushButton("+")
        btn_add_task.setFixedSize(24, 24)
        btn_add_task.setStyleSheet("background-color: transparent; color: #a855f7; font-weight: bold; font-size: 16px;")
        btn_add_task.clicked.connect(self.show_add_task_input)
        task_header.addWidget(btn_add_task)
        
        s_layout.addLayout(task_header)
        
        # Input hidden for new tasks
        self.task_input_container = QWidget()
        ti_layout = QHBoxLayout(self.task_input_container)
        ti_layout.setContentsMargins(0, 0, 0, 0)
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("New task...")
        self.task_input.setStyleSheet("background-color: #25252b; border: 1px solid #3f3f46; border-radius: 6px; padding: 5px; color: white;")
        self.task_input.returnPressed.connect(self.add_task)
        ti_layout.addWidget(self.task_input)
        self.task_input_container.hide()
        s_layout.addWidget(self.task_input_container)
        
        # Scroll Area untuk Tasks
        task_scroll = QScrollArea()
        task_scroll.setWidgetResizable(True)
        task_scroll.setMaximumHeight(150)
        task_scroll.setStyleSheet("background-color: transparent; border: none;")
        
        self.task_container = QWidget()
        self.task_list_layout = QVBoxLayout(self.task_container)
        self.task_list_layout.setContentsMargins(0, 0, 0, 0)
        self.task_list_layout.setSpacing(2)
        self.task_list_layout.addStretch()
        
        task_scroll.setWidget(self.task_container)
        s_layout.addWidget(task_scroll)
        
        self.load_tasks()
        
        s_layout.addSpacing(15)
        
        # Section Title: OLDER
        lbl_older = QLabel("<b style='color:#71717a; font-size: 11px; letter-spacing: 1px;'>FOLDER</b>")
        s_layout.addWidget(lbl_older)
        
        # Scroll Area untuk Chat History
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("background-color: transparent; border: none;")
        
        chat_container = QWidget()
        self.chat_layout = QVBoxLayout(chat_container)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_layout.setSpacing(2)
        self.chat_layout.addStretch()
        
        scroll_area.setWidget(chat_container)
        s_layout.addWidget(scroll_area)
        
        # Footer Profile (Dynamic User Info)
        s_layout.addSpacing(10)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #2d2d35;")
        s_layout.addWidget(line)
        
        profile_layout = QHBoxLayout()
        profile_layout.setContentsMargins(0, 10, 0, 0)
        
        lbl_avatar = QLabel("👩🏽")
        lbl_avatar.setStyleSheet("font-size: 24px; background: #3f3f46; border-radius: 18px; padding: 4px;")
        lbl_avatar.setFixedSize(36, 36)
        lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        profile_info = QVBoxLayout()
        profile_info.setSpacing(0)
        lbl_name = QLabel(f"<b style='color: white; font-size: 13px;'>{self.user_name}</b>")
        lbl_role = QLabel(f"<span style='color: #71717a; font-size: 10px;'>{self.user_role}</span>")
        profile_info.addWidget(lbl_name)
        profile_info.addWidget(lbl_role)
        
        profile_layout.addWidget(lbl_avatar)
        profile_layout.addLayout(profile_info)
        profile_layout.addStretch()
        profile_layout.addWidget(QLabel("<span style='color:#71717a;'>^</span>"))
        
        s_layout.addLayout(profile_layout)

        layout.addWidget(sidebar)

        # --- MAIN CHAT AREA (Kanan) ---
        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header Chat (Model Selector)
        header_chat = QFrame()
        header_chat.setStyleSheet("background-color: #1a1a1f; border-bottom: 1px solid #2d2d35;")
        hc_layout = QHBoxLayout(header_chat)
        hc_layout.setContentsMargins(20, 15, 20, 15)
        
        hc_layout.addWidget(QLabel("<b style='color: #e1e1e6; font-size: 16px;'>Chat</b>"))
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
        
        self.display = QTextBrowser()
        self.display.setObjectName("ChatDisplay")
        cdc_layout.addWidget(self.display)
        
        self.loading_anim = LoadingAnimation()
        cdc_layout.addWidget(self.loading_anim)
        
        self.chat_stack.addWidget(self.welcome_widget)
        self.chat_stack.addWidget(self.chat_display_container)
        
        c_layout.addWidget(self.chat_stack)

        # Input Field ala gambar
        input_container = QFrame()
        input_container.setObjectName("InputContainer")
        input_h = QHBoxLayout(input_container)
        
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

    def show_add_task_input(self):
        self.task_input_container.setVisible(not self.task_input_container.isVisible())
        if self.task_input_container.isVisible():
            self.task_input.setFocus()

    def add_task(self):
        title = self.task_input.text().strip()
        if not title or not self.db: return
        
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO tasks (title) VALUES (%s)", (title,))
        self.db.commit()
        
        self.task_input.clear()
        self.task_input_container.hide()
        self.load_tasks()

    def delete_task(self, task_id):
        if not self.db: return
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        self.db.commit()
        self.load_tasks()

    def load_tasks(self):
        # Clear existing tasks
        for i in reversed(range(self.task_list_layout.count())): 
            widget = self.task_list_layout.itemAt(i).widget()
            if widget: widget.deleteLater()
            
        if not self.db: return
        
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        tasks = cursor.fetchall()
        
        for task in tasks:
            t_frame = QFrame()
            t_frame.setStyleSheet("""
                QFrame { background-color: #1a1a1f; border-radius: 6px; }
                QFrame:hover { background-color: #25252b; }
            """)
            t_layout = QHBoxLayout(t_frame)
            t_layout.setContentsMargins(10, 8, 10, 8)
            
            lbl_title = QLabel(f"<span style='color: #e1e1e6; font-size: 12px;'>{task['title']}</span>")
            t_layout.addWidget(lbl_title)
            t_layout.addStretch()
            
            btn_del = QPushButton("🗑")
            btn_del.setFixedSize(20, 20)
            btn_del.setStyleSheet("color: #ef4444; background: transparent; border: none;")
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.clicked.connect(lambda checked, tid=task['id']: self.delete_task(tid))
            t_layout.addWidget(btn_del)
            
            self.task_list_layout.insertWidget(self.task_list_layout.count() - 1, t_frame)

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

    def append_message(self, sender, text, save=True):
        is_user = sender == "You"
        formatted_text = text.replace('\n', '<br>')
        
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
            if is_user:
                self.chat_sessions[self.current_session_id]["llm_history"].append(f"User: {text}")
            else:
                self.chat_sessions[self.current_session_id]["llm_history"].append(f"AI: {text}")

        if is_user:
            # Pesan Pengguna: Rata Kanan, Bubble Pink/Purple solid untuk mensimulasikan gradient
            full_html = f"""
            <table width="100%" style="margin-top: 10px; margin-bottom: 10px;">
                <tr>
                    <td align="right" valign="top">
                        <table style="background-color: #b538b0; border-radius: 18px;">
                            <tr>
                                <td style="padding: 12px 18px; color: #ffffff; font-size: 14px; line-height: 1.4;">
                                    {formatted_text}
                                </td>
                            </tr>
                        </table>
                    </td>
                    <td width="45" align="center" valign="top">
                        <div style="font-size: 24px;">👱🏻‍♀️</div>
                    </td>
                </tr>
            </table>
            """
        else:
            # Pesan AI: Rata Kiri, Bubble Abu-abu Gelap tanpa style border di kiri, sesuai image
            full_html = f"""
            <table width="100%" style="margin-top: 10px; margin-bottom: 10px;">
                <tr>
                    <td width="45" align="center" valign="top">
                        <div style="font-size: 20px; background-color: #111; border-radius: 12px; padding: 5px;">✨</div>
                    </td>
                    <td align="left" valign="top">
                        <table style="background-color: #202020; border-radius: 18px;">
                            <tr>
                                <td style="padding: 12px 18px; color: #e1e1e6; font-size: 14px; line-height: 1.4;">
                                    {formatted_text}
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
            """

        self.display.append(full_html)
        self.display.moveCursor(QTextCursor.MoveOperation.End)

    def handle_send(self):
        text = self.input_field.text().strip()
        if not text: return
        
        self.chat_stack.setCurrentIndex(1)
        self.append_message("You", text, save=True)
        self.input_field.clear()
        
        context = "\n".join(self.chat_sessions[self.current_session_id]["llm_history"][-10:])
        
        self.loading_anim.show()
        
        self.worker = ChatWorker(self.model_box.currentText(), context)
        self.worker.response_ready.connect(self.handle_response)
        self.worker.start()

    def handle_response(self, response):
        self.loading_anim.hide()
        self.append_message("Ollama AI", response, save=True)

    def reset_chat(self):
        self.display.clear()
        self.current_session_id = None
        self.chat_stack.setCurrentIndex(0)

    def load_chat(self, session_id):
        self.display.clear()
        self.current_session_id = session_id
        self.chat_stack.setCurrentIndex(1)
        session_data = self.chat_sessions[session_id]
        
        for sender, text in session_data["history"]:
            self.append_message(sender, text, save=False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Menampilkan Setup Profile Dialog terlebih dahulu
    setup_dialog = ProfileSetupDialog()
    if setup_dialog.exec() == QDialog.DialogCode.Accepted or True: # Jika user menutup window secara paksa sekalipun, aplikasi tetap lanjut.
        window = OllamaAIApp(user_name=setup_dialog.user_name, user_role=setup_dialog.user_role)
        window.show()
        sys.exit(app.exec())