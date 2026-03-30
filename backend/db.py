import sqlite3

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    answer TEXT
)
""")

def save_chat(q, a):
    cursor.execute("INSERT INTO chats (question, answer) VALUES (?, ?)", (q, a))
    conn.commit()

def get_history():
    cursor.execute("SELECT * FROM chats ORDER BY id DESC LIMIT 5")
    return cursor.fetchall()
