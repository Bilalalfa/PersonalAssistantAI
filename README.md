# Ollama Vision - Personal Assistant AI 🤖📸

**Ollama Vision** is a modern personal assistant application that combines the power of Large Language Models (LLMs) from Ollama with Computer Vision capabilities. Built with Python and PyQt6, it features a modular architecture that separates the UI, AI integration, and database management, delivering a responsive and aesthetically pleasing experience.

---

## ✨ Key Features

- **💬 AI Chat Assistant**: Interact with various local LLMs via Ollama.
- **👁️ Vision Support**: Upload images (PNG, JPG, WEBP) for analysis by vision-capable models (e.g., Llava).
- **📄 Document Upload**: Easily attach documents or images using the new **Plus (+)** menu in the chat interface.
- **📅 Task Manager**: Manage your daily tasks with full CRUD (Create, Read, Update, Delete) functionality.
- **🗓️ Academic Calendar**: A built-in calendar dashboard to monitor task deadlines and schedules.
- **🗂️ Chat History**: Save and revisit previous chat sessions through the interactive sidebar.
- **🎨 Modern UI**: Elegant Dark Mode interface with glassmorphism-inspired design, card-based layouts, and smooth animations.

---

## 🛠️ Technology Stack

- **Language**: [Python 3.10+](https://www.python.org/)
- **UI Framework**: [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- **AI Integration**: [LangChain Ollama](https://python.langchain.com/docs/integrations/llms/ollama/)
- **Local LLM Runner**: [Ollama](https://ollama.com/)
- **Database**: [MySQL](https://www.mysql.com/) (via `mysql-connector-python`)
- **Icons**: [QtAwesome](https://github.com/spyder-ide/qtawesome)

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have the following installed:
- **Python**: [Download here](https://www.python.org/downloads/)
- **Ollama**: [Download here](https://ollama.com/download)
- **XAMPP / MySQL Server**: Ensure MySQL is running on `localhost:3306`.

### 2. Install Dependencies
Run the following command in your terminal:
```bash
pip install pyqt6 langchain_ollama mysql-connector-python qtawesome
```

### 3. Database Configuration
The application automatically creates the `ollama_assistant` database and `tasks` table on its first run. Ensure your MySQL server is active with the `root` user (default for XAMPP).

### 4. Downloading AI Models
To use the vision features, you must pull a vision-capable model:
```bash
ollama pull llava
```

### 5. Running the Application
```bash
python app.py
```

---

## 📁 Project Structure

```text
PersonalAssistantAI/
├── app.py                      # Main entry point & Controller
├── UI/
│   ├── ui_components.py          # PyQt6 interface definitions
│   └── style.py                  # CSS/QSS configurations and theme
├── ai_integration/
│   └── ai_engine.py              # AI logic (ChatWorker, Vision encoding)
├── Database/
│   └── db_handler.py             # Database management (Connection, CRUD)
├── requirements.txt            # List of dependencies
└── README.md                   # Project documentation
```

---

## 📋 Task Manager Features
- **Add Task**: Enter a description and select a deadline on the calendar.
- **Status Tracking**: Mark tasks as completed to highlight them in green.
- **Filtering**: Click any date on the calendar to see tasks specific to that day.
- **Persistence**: All tasks are stored locally in your MySQL database.

---

## 📝 Usage Notes
- Make sure the **Ollama service** is running in the background for AI features to work.
- Use the **(+) icon** in the chat bar to switch between uploading **Images** (for analysis) and **Documents** (as context references).
- For the best vision experience, models like `llava` or `moondream` are recommended.

---

Developed for **Gorsel Programlama II** - Semester 6.
