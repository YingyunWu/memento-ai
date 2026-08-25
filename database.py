import sqlite3

connection = sqlite3.connect("memento.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS journals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    journal_date TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    journal_id INTEGER NOT NULL,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT
)
""")

# Add updated_at if it does not exist
cursor.execute("PRAGMA table_info(memories)")
columns = [column[1] for column in cursor.fetchall()]

if "updated_at" not in columns:
    cursor.execute("""
    ALTER TABLE memories
    ADD COLUMN updated_at TEXT
    """)

connection.commit()
connection.close()

print("Memento AI database initialized.")