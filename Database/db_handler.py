import mysql.connector
from mysql.connector import errorcode

def get_db_connection():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ollama_assistant",
            use_pure=True,
            connection_timeout=5
        )
        return db
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            # Database doesn't exist, create it
            return create_database()
        else:
            print(f"Error Database: {err}")
            return None
    except Exception as e:
        print(f"Unexpected crash in connection: {e}")
        return None

def create_database():
    try:
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
        return get_db_connection()
    except Exception as e:
        print(f"Crash during DB creation: {e}")
        return None

def init_db(db):
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                status ENUM('pending', 'completed') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deadline DATE NULL
            )
        """)
        db.commit()
    except Exception as e:
        print(f"Error creating tables: {e}")

def check_db_schema(db):
    if not db: return
    cursor = db.cursor()
    try:
        cursor.execute("SHOW COLUMNS FROM tasks LIKE 'deadline'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE tasks ADD COLUMN deadline DATE NULL")
        db.commit()
    except: pass

def load_tasks_from_db(db, filter_date=None):
    check_db_schema(db)
    if not db: return []
    cursor = db.cursor(dictionary=True)
    if filter_date:
        # Ubah DESC menjadi ASC
        cursor.execute("SELECT * FROM tasks WHERE deadline = %s ORDER BY created_at ASC", (filter_date,))
    else:
        # Ubah DESC menjadi ASC
        cursor.execute("SELECT * FROM tasks ORDER BY created_at ASC")
    return cursor.fetchall()

def add_task_to_db(db, title, deadline):
    if not db: return False
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO tasks (title, deadline) VALUES (%s, %s)", (title, deadline))
        db.commit()
        return True
    except Exception as e:
        print(f"Error adding task: {e}")
        return False

def delete_task_from_db(db, task_id):
    if not db: return False
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        db.commit()
        return True
    except Exception as e:
        print(f"Error deleting task: {e}")
        return False

def complete_task_in_db(db, task_id):
    if not db: return False
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = %s", (task_id,))
        db.commit()
        return True
    except Exception as e:
        print(f"Error completing task: {e}")
        return False
