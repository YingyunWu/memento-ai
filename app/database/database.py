from pathlib import Path
import sqlite3
from datetime import datetime


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "memento.db"


# ============================================================
# Database connection
# ============================================================

def get_connection():
    """
    Create a connection to the Memento AI database.
    """

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# Timestamp
# ============================================================

def current_timestamp():
    """
    Return the current timestamp.
    """

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# ============================================================
# Initialize database
# ============================================================

def initialize_database():
    """
    Create database tables if they do not exist.

    Also performs lightweight migrations for
    existing databases.
    """

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # Journals
    # --------------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        journal_date TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    # --------------------------------------------------------
    # Memories
    # --------------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        journal_id INTEGER NOT NULL,
        memory_type TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT,
        source_type TEXT,
        file_path TEXT,
        platform TEXT,

        FOREIGN KEY (journal_id)
        REFERENCES journals(id)
    )
    """)

    # --------------------------------------------------------
    # Memory migrations
    # --------------------------------------------------------

    cursor.execute(
        "PRAGMA table_info(memories)"
    )

    memory_columns = [
        column[1]
        for column in cursor.fetchall()
    ]

    if "updated_at" not in memory_columns:

        cursor.execute("""
        ALTER TABLE memories
        ADD COLUMN updated_at TEXT
        """)

    if "source_type" not in memory_columns:

        cursor.execute("""
        ALTER TABLE memories
        ADD COLUMN source_type TEXT
        """)

    if "file_path" not in memory_columns:

        cursor.execute("""
        ALTER TABLE memories
        ADD COLUMN file_path TEXT
        """)

    if "platform" not in memory_columns:

        cursor.execute("""
        ALTER TABLE memories
        ADD COLUMN platform TEXT
        """)

    # --------------------------------------------------------
    # Analyses
    # --------------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        memory_id INTEGER NOT NULL,

        analysis_type TEXT NOT NULL,

        result TEXT,

        confidence REAL,

        status TEXT NOT NULL DEFAULT 'pending',

        reason TEXT,

        created_at TEXT NOT NULL,

        FOREIGN KEY (memory_id)
        REFERENCES memories(id)
        ON DELETE CASCADE
    )
    """)

    # --------------------------------------------------------
    # Analysis migrations
    # --------------------------------------------------------

    cursor.execute(
        "PRAGMA table_info(analyses)"
    )

    analysis_columns = [
        column[1]
        for column in cursor.fetchall()
    ]

    if "result" not in analysis_columns:

        cursor.execute("""
        ALTER TABLE analyses
        ADD COLUMN result TEXT
        """)

    if "confidence" not in analysis_columns:

        cursor.execute("""
        ALTER TABLE analyses
        ADD COLUMN confidence REAL
        """)

    if "status" not in analysis_columns:

        cursor.execute("""
        ALTER TABLE analyses
        ADD COLUMN status TEXT NOT NULL
        DEFAULT 'pending'
        """)

    if "reason" not in analysis_columns:

        cursor.execute("""
        ALTER TABLE analyses
        ADD COLUMN reason TEXT
        """)

    if "created_at" not in analysis_columns:

        cursor.execute("""
        ALTER TABLE analyses
        ADD COLUMN created_at TEXT
        """)

    # --------------------------------------------------------
    # Backfill existing memories
    # --------------------------------------------------------

    cursor.execute("""
    UPDATE memories
    SET source_type = 'text'
    WHERE source_type IS NULL
    """)

    cursor.execute("""
    UPDATE memories
    SET updated_at = created_at
    WHERE updated_at IS NULL
    """)

    connection.commit()
    connection.close()

    print(
        "Memento AI database initialized."
    )


# ============================================================
# Journal helpers
# ============================================================

def get_or_create_journal(journal_date):
    """
    Get an existing journal or create a new one.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT *
    FROM journals
    WHERE journal_date = ?
    """, (journal_date,))

    journal = cursor.fetchone()

    if journal:

        connection.close()

        return journal

    timestamp = current_timestamp()

    cursor.execute("""
    INSERT INTO journals (
        journal_date,
        created_at,
        updated_at
    )
    VALUES (?, ?, ?)
    """, (
        journal_date,
        timestamp,
        timestamp,
    ))

    journal_id = cursor.lastrowid

    connection.commit()

    cursor.execute("""
    SELECT *
    FROM journals
    WHERE id = ?
    """, (journal_id,))

    journal = cursor.fetchone()

    connection.close()

    return journal


# ============================================================
# Add memory
# ============================================================

def add_memory(
    journal_date,
    memory_type,
    content="",
    source_type="text",
    file_path=None,
    platform=None,
):
    """
    Add a memory to a journal.
    """

    journal = get_or_create_journal(
        journal_date
    )

    connection = get_connection()
    cursor = connection.cursor()

    timestamp = current_timestamp()

    cursor.execute("""
    INSERT INTO memories (
        journal_id,
        memory_type,
        content,
        created_at,
        updated_at,
        source_type,
        file_path,
        platform
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        journal["id"],
        memory_type,
        content,
        timestamp,
        timestamp,
        source_type,
        file_path,
        platform,
    ))

    memory_id = cursor.lastrowid

    cursor.execute("""
    UPDATE journals
    SET updated_at = ?
    WHERE id = ?
    """, (
        timestamp,
        journal["id"],
    ))

    connection.commit()
    connection.close()

    return memory_id


# ============================================================
# Get memories
# ============================================================

def get_memories(journal_date):
    """
    Get all memories for a journal date.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT
        memories.id,
        memories.journal_id,
        memories.memory_type,
        memories.content,
        memories.created_at,
        memories.updated_at,
        memories.source_type,
        memories.file_path,
        memories.platform,
        journals.journal_date
    FROM memories
    JOIN journals
        ON memories.journal_id = journals.id
    WHERE journals.journal_date = ?
    ORDER BY memories.created_at ASC
    """, (journal_date,))

    memories = cursor.fetchall()

    connection.close()

    return memories


# ============================================================
# Get single memory
# ============================================================

def get_memory(memory_id):
    """
    Get one memory by ID.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT
        memories.id,
        memories.journal_id,
        memories.memory_type,
        memories.content,
        memories.created_at,
        memories.updated_at,
        memories.source_type,
        memories.file_path,
        memories.platform,
        journals.journal_date
    FROM memories
    JOIN journals
        ON memories.journal_id = journals.id
    WHERE memories.id = ?
    """, (memory_id,))

    memory = cursor.fetchone()

    connection.close()

    return memory


# ============================================================
# Update memory
# ============================================================

def update_memory(
    memory_id,
    new_content=None,
    new_file_path=None,
    new_platform=None,
):
    """
    Update an existing memory.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT *
    FROM memories
    WHERE id = ?
    """, (memory_id,))

    memory = cursor.fetchone()

    if memory is None:

        connection.close()

        raise ValueError(
            f"Memory with ID {memory_id} does not exist."
        )

    content = (
        new_content
        if new_content is not None
        else memory["content"]
    )

    file_path = (
        new_file_path
        if new_file_path is not None
        else memory["file_path"]
    )

    platform = (
        new_platform
        if new_platform is not None
        else memory["platform"]
    )

    timestamp = current_timestamp()

    cursor.execute("""
    UPDATE memories
    SET
        content = ?,
        file_path = ?,
        platform = ?,
        updated_at = ?
    WHERE id = ?
    """, (
        content,
        file_path,
        platform,
        timestamp,
        memory_id,
    ))

    cursor.execute("""
    UPDATE journals
    SET updated_at = ?
    WHERE id = ?
    """, (
        timestamp,
        memory["journal_id"],
    ))

    connection.commit()
    connection.close()

    return True


# ============================================================
# Delete memory
# ============================================================

def delete_memory(memory_id):
    """
    Delete an existing memory.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT *
    FROM memories
    WHERE id = ?
    """, (memory_id,))

    memory = cursor.fetchone()

    if memory is None:

        connection.close()

        raise ValueError(
            f"Memory with ID {memory_id} does not exist."
        )

    journal_id = memory["journal_id"]

    cursor.execute("""
    DELETE FROM memories
    WHERE id = ?
    """, (memory_id,))

    timestamp = current_timestamp()

    cursor.execute("""
    UPDATE journals
    SET updated_at = ?
    WHERE id = ?
    """, (
        timestamp,
        journal_id,
    ))

    connection.commit()
    connection.close()

    return True


# ============================================================
# Add analysis
# ============================================================

def add_analysis(
    memory_id,
    analysis_type,
    result=None,
    confidence=None,
    status="pending",
    reason=None,
):
    """
    Add an AI analysis result for a memory.

    Supported statuses:

        pending
        completed
        unknown
        failed
    """

    allowed_statuses = {
        "pending",
        "completed",
        "unknown",
        "failed",
    }

    if status not in allowed_statuses:

        raise ValueError(
            "Invalid analysis status. "
            "Allowed statuses: "
            + ", ".join(
                sorted(allowed_statuses)
            )
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT id
    FROM memories
    WHERE id = ?
    """, (memory_id,))

    memory = cursor.fetchone()

    if memory is None:

        connection.close()

        raise ValueError(
            f"Memory with ID {memory_id} does not exist."
        )

    timestamp = current_timestamp()

    cursor.execute("""
    INSERT INTO analyses (
        memory_id,
        analysis_type,
        result,
        confidence,
        status,
        reason,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        memory_id,
        analysis_type,
        result,
        confidence,
        status,
        reason,
        timestamp,
    ))

    analysis_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return analysis_id


# ============================================================
# Get analyses
# ============================================================

def get_analyses(memory_id):
    """
    Get all analyses associated with a memory.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT
        id,
        memory_id,
        analysis_type,
        result,
        confidence,
        status,
        reason,
        created_at
    FROM analyses
    WHERE memory_id = ?
    ORDER BY created_at ASC
    """, (memory_id,))

    analyses = cursor.fetchall()

    connection.close()

    return analyses


# ============================================================
# Get single analysis
# ============================================================

def get_analysis(analysis_id):
    """
    Get one analysis by ID.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT
        id,
        memory_id,
        analysis_type,
        result,
        confidence,
        status,
        reason,
        created_at
    FROM analyses
    WHERE id = ?
    """, (analysis_id,))

    analysis = cursor.fetchone()

    connection.close()

    return analysis


# ============================================================
# Update analysis
# ============================================================

def update_analysis(
    analysis_id,
    result=None,
    confidence=None,
    status=None,
    reason=None,
):
    """
    Update an existing analysis.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT *
    FROM analyses
    WHERE id = ?
    """, (analysis_id,))

    analysis = cursor.fetchone()

    if analysis is None:

        connection.close()

        raise ValueError(
            f"Analysis with ID {analysis_id} does not exist."
        )

    allowed_statuses = {
        "pending",
        "completed",
        "unknown",
        "failed",
    }

    new_status = (
        status
        if status is not None
        else analysis["status"]
    )

    if new_status not in allowed_statuses:

        connection.close()

        raise ValueError(
            "Invalid analysis status."
        )

    new_result = (
        result
        if result is not None
        else analysis["result"]
    )

    new_confidence = (
        confidence
        if confidence is not None
        else analysis["confidence"]
    )

    new_reason = (
        reason
        if reason is not None
        else analysis["reason"]
    )

    cursor.execute("""
    UPDATE analyses
    SET
        result = ?,
        confidence = ?,
        status = ?,
        reason = ?
    WHERE id = ?
    """, (
        new_result,
        new_confidence,
        new_status,
        new_reason,
        analysis_id,
    ))

    connection.commit()
    connection.close()

    return True


# ============================================================
# Delete analysis
# ============================================================

def delete_analysis(analysis_id):
    """
    Delete an existing analysis.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT id
    FROM analyses
    WHERE id = ?
    """, (analysis_id,))

    analysis = cursor.fetchone()

    if analysis is None:

        connection.close()

        raise ValueError(
            f"Analysis with ID {analysis_id} does not exist."
        )

    cursor.execute("""
    DELETE FROM analyses
    WHERE id = ?
    """, (analysis_id,))

    connection.commit()
    connection.close()

    return True


# ============================================================
# Run directly
# ============================================================

if __name__ == "__main__":
    initialize_database()