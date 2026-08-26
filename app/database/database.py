import sqlite3
from datetime import datetime
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Local data directory
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# SQLite database path
DB_PATH = BASE_DIR / "memento.db"


def get_connection():
    """
    Create and return a connection to the Memento AI database.
    """
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """
    Create the database tables if they do not already exist.
    """
    connection = get_connection()
    cursor = connection.cursor()

    # Journals represent one calendar day.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS journals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            journal_date TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    # Memories belong to a journal.
    # memory_type can be:
    # text / photo / music / video
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            journal_id INTEGER NOT NULL,
            memory_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT,

            FOREIGN KEY (journal_id)
                REFERENCES journals(id)
                ON DELETE CASCADE
        )
        """
    )

    connection.commit()
    connection.close()

    print("Memento AI database initialized.")


def get_or_create_journal(journal_date):
    """
    Find a journal by date.
    If it does not exist, create it.

    Returns:
        journal_id
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM journals
        WHERE journal_date = ?
        """,
        (journal_date,)
    )

    journal = cursor.fetchone()

    if journal:
        connection.close()
        return journal["id"]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO journals (
            journal_date,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?)
        """,
        (journal_date, now, now)
    )

    journal_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return journal_id


def add_memory(journal_date, memory_type, content):
    """
    Add a new memory to a journal.

    memory_type:
        text
        photo
        music
        video
    """
    journal_id = get_or_create_journal(journal_date)

    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO memories (
            journal_id,
            memory_type,
            content,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            journal_id,
            memory_type,
            content,
            now,
            now
        )
    )

    memory_id = cursor.lastrowid

    cursor.execute(
        """
        UPDATE journals
        SET updated_at = ?
        WHERE id = ?
        """,
        (now, journal_id)
    )

    connection.commit()
    connection.close()

    return memory_id


def get_memories(journal_date):
    """
    Get all memories belonging to a journal date.

    Returns:
        list of sqlite3.Row objects
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            memories.id,
            memories.journal_id,
            memories.memory_type,
            memories.content,
            memories.created_at,
            memories.updated_at
        FROM memories
        JOIN journals
            ON memories.journal_id = journals.id
        WHERE journals.journal_date = ?
        ORDER BY memories.created_at ASC
        """,
        (journal_date,)
    )

    memories = cursor.fetchall()

    connection.close()

    return memories


def get_memory(memory_id):
    """
    Get one memory by its ID.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            memories.id,
            memories.journal_id,
            memories.memory_type,
            memories.content,
            memories.created_at,
            memories.updated_at,
            journals.journal_date
        FROM memories
        JOIN journals
            ON memories.journal_id = journals.id
        WHERE memories.id = ?
        """,
        (memory_id,)
    )

    memory = cursor.fetchone()

    connection.close()

    return memory


def update_memory(memory_id, new_content):
    """
    Update an existing memory.
    """
    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        UPDATE memories
        SET content = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            new_content,
            now,
            memory_id
        )
    )

    if cursor.rowcount == 0:
        connection.close()
        return False

    # Also update the journal's updated_at timestamp.
    cursor.execute(
        """
        SELECT journal_id
        FROM memories
        WHERE id = ?
        """,
        (memory_id,)
    )

    memory = cursor.fetchone()

    if memory:
        cursor.execute(
            """
            UPDATE journals
            SET updated_at = ?
            WHERE id = ?
            """,
            (now, memory["journal_id"])
        )

    connection.commit()
    connection.close()

    return True


def delete_memory(memory_id):
    """
    Delete a memory by ID.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT journal_id
        FROM memories
        WHERE id = ?
        """,
        (memory_id,)
    )

    memory = cursor.fetchone()

    if not memory:
        connection.close()
        return False

    journal_id = memory["journal_id"]

    cursor.execute(
        """
        DELETE FROM memories
        WHERE id = ?
        """,
        (memory_id,)
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        UPDATE journals
        SET updated_at = ?
        WHERE id = ?
        """,
        (now, journal_id)
    )

    connection.commit()
    connection.close()

    return True


if __name__ == "__main__":
    initialize_database()