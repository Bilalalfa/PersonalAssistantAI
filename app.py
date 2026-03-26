import sys
import os
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from UI.style import STYLE_SHEET
from ai_integration.ai_engine import ChatWorker, encode_image
from Database.db_handler import (get_db_connection, init_db, load_tasks_from_db, 
                         add_task_to_db, delete_task_from_db, complete_task_in_db)
from UI.ui_components import MainInterface, ProfileSetupDialog

class PersonalAssistantApp:
    def __init__(self, user_name, user_role):
        self.user_name = user_name
        self.user_role = user_role
        
        # Initialize Database
        self.db = get_db_connection()
        if self.db:
            init_db(self.db)
        
        # Initialize UI
        self.ui = MainInterface(user_name, user_role)
        self.setup_connections()
        
        # State
        self.chat_sessions = {}
        self.current_session_id = None
        self.session_counter = 0
        
        self.ui.show()

    def setup_connections(self):
        # UI Signals to App Logic
        self.ui.send_message_signal.connect(self.handle_send)
        self.ui.new_chat_signal.connect(self.reset_chat)
        self.ui.show_task_mgr_signal.connect(self.show_task_manager)
        self.ui.add_task_signal.connect(self.tm_add_task)
        self.ui.delete_task_signal.connect(self.tm_delete_task)
        self.ui.complete_task_signal.connect(self.tm_complete_task)
        self.ui.filter_tasks_signal.connect(self.filter_tasks)
        self.ui.load_all_tasks_signal.connect(self.load_all_tasks)
        self.ui.chat_session_selected_signal.connect(self.load_chat)

    # --- CHAT LOGIC ---
    def handle_send(self, text, img_path):
        if not text and not img_path: return
        
        # Move to Chat Stack
        self.ui.chat_stack.setCurrentIndex(1)
        self.ui.input_container.show()
        
        # Display User Message
        self.append_message("You", text, save=True, image_path=img_path)
        
        # Prepare Context
        if self.current_session_id:
            context = "\n".join(self.chat_sessions[self.current_session_id]["llm_history"][-10:])
        else:
            context = text
        
        # Prepare Images
        base64_images = []
        if img_path:
            encoded = encode_image(img_path)
            if encoded: base64_images.append(encoded)
        
        self.ui.loading_anim.show()
        
        # Start AI Worker
        model = self.ui.model_box.currentText()
        self.worker = ChatWorker(model, context, images=base64_images if base64_images else None)
        self.worker.response_ready.connect(self.handle_response)
        self.worker.start()

    def handle_response(self, response):
        self.ui.loading_anim.hide()
        self.append_message("Ollama AI", response, save=True)

    def append_message(self, sender, text, save=True, image_path=None):
        is_user = sender == "You"
        formatted_text = text.replace('\n', '<br>')
        
        bubble_container = self.ui.create_chat_bubble(is_user, formatted_text, image_path)
        
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
                self.ui.add_sidebar_button(self.current_session_id, name)
            
            self.chat_sessions[self.current_session_id]["history"].append((sender, text))
            msg_str = f"{sender}: {text}"
            if image_path: msg_str += " [Image Attached]"
            self.chat_sessions[self.current_session_id]["llm_history"].append(msg_str)

        self.ui.chat_history_layout.insertWidget(self.ui.chat_history_layout.count() - 1, bubble_container)
        scrollbar = self.ui.chat_scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def reset_chat(self):
        self.clear_chat_widgets()
        self.current_session_id = None
        self.ui.chat_stack.setCurrentIndex(0)
        self.ui.input_container.show()

    def load_chat(self, session_id):
        self.clear_chat_widgets()
        self.current_session_id = session_id
        self.ui.chat_stack.setCurrentIndex(1)
        self.ui.input_container.show()
        
        session_data = self.chat_sessions[session_id]
        for sender, text in session_data["history"]:
            self.append_message(sender, text, save=False)

    def clear_chat_widgets(self):
        while self.ui.chat_history_layout.count() > 1:
            item = self.ui.chat_history_layout.takeAt(0)
            if item and item.widget(): item.widget().deleteLater()

    # --- TASK MANAGER LOGIC ---
    def show_task_manager(self):
        self.ui.chat_stack.setCurrentIndex(2)
        self.ui.input_container.hide()
        self.load_all_tasks()

    def load_all_tasks(self):
        self.tm_update_table(load_tasks_from_db(self.db))

    def filter_tasks(self, date_str):
        self.tm_update_table(load_tasks_from_db(self.db, filter_date=date_str))

    def tm_update_table(self, tasks):
        self.ui.tm_table.setRowCount(0)
        for i, task in enumerate(tasks):
            from PyQt6.QtWidgets import QTableWidgetItem
            self.ui.tm_table.insertRow(i)
            self.ui.tm_table.setItem(i, 0, QTableWidgetItem(str(task['id'])))
            self.ui.tm_table.setItem(i, 1, QTableWidgetItem(task['title']))
            
            status_item = QTableWidgetItem(task['status'].upper())
            status_item.setForeground(QColor("#10b981") if task['status'] == 'completed' else QColor("#f59e0b"))
            self.ui.tm_table.setItem(i, 2, status_item)
            
            self.ui.tm_table.setItem(i, 3, QTableWidgetItem(task['created_at'].strftime("%Y-%m-%d %H:%M")))
            self.ui.tm_table.setItem(i, 4, QTableWidgetItem(str(task['deadline']) if task['deadline'] else "No Deadline"))

    def tm_add_task(self, title, deadline):
        if not title: return
        if not self.db:
            QMessageBox.warning(self.ui, "Error", "Database disconnected.")
            return
        if add_task_to_db(self.db, title, deadline):
            self.ui.tm_input.clear()
            self.load_all_tasks()

    def tm_delete_task(self, task_id):
        reply = QMessageBox.question(self.ui, 'Delete', 'Are you sure?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if delete_task_from_db(self.db, task_id):
                self.load_all_tasks()

    def tm_complete_task(self, task_id):
        if complete_task_in_db(self.db, task_id):
            self.load_all_tasks()

# --- MAIN ENTRY POINT ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    setup_dialog = ProfileSetupDialog()
    if setup_dialog.exec() == QDialog.DialogCode.Accepted:
        controller = PersonalAssistantApp(setup_dialog.user_name, setup_dialog.user_role)
        sys.exit(app.exec())
