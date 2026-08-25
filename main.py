import sqlite3
from datetime import datetime
from pathlib import Path
import shutil
import tkinter as tk
from tkinter import filedialog


BASE_DIR = Path(__file__).resolve().parent
MEDIA_DIR = BASE_DIR / "data" / "media"


def connect_database():
    return sqlite3.connect(BASE_DIR / "memento.db")


def get_or_create_journal(connection, journal_date):
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM journals WHERE journal_date = ?",
        (journal_date,)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO journals (journal_date, created_at, updated_at)
        VALUES (?, ?, ?)
        """,
        (journal_date, current_time, current_time)
    )

    connection.commit()

    return cursor.lastrowid


def update_journal_time(connection, journal_id):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE journals
        SET updated_at = ?
        WHERE id = ?
        """,
        (current_time, journal_id)
    )


def choose_memory_type():
    print("\nChoose memory type:")
    print("1. Text")
    print("2. Photo")
    print("3. Music")
    print("4. Video")

    choice = input("\nChoose an option: ")

    memory_types = {
        "1": "text",
        "2": "photo",
        "3": "music",
        "4": "video"
    }

    return memory_types.get(choice)


def choose_photo():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Choose a photo",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.gif *.webp"),
            ("All files", "*.*")
        ]
    )

    root.destroy()

    return file_path


def save_photo(file_path, journal_date):
    source = Path(file_path)

    if not source.exists():
        print("\nPhoto file does not exist.")
        return None

    journal_media_dir = MEDIA_DIR / journal_date
    journal_media_dir.mkdir(parents=True, exist_ok=True)

    destination = journal_media_dir / source.name

    # Avoid overwriting an existing photo
    if destination.exists():
        timestamp = datetime.now().strftime("%H%M%S")
        destination = (
            journal_media_dir
            / f"{source.stem}_{timestamp}{source.suffix}"
        )

    shutil.copy2(source, destination)

    return str(destination.relative_to(BASE_DIR))


def add_memory():
    journal_date = input("Enter journal date (YYYY-MM-DD): ")

    memory_type = choose_memory_type()

    if memory_type is None:
        print("\nInvalid memory type.")
        return

    if memory_type == "text":

        content = input("\nWhat would you like to write? ")

    elif memory_type == "photo":

        print("\nPlease choose a photo from your computer.")

        file_path = choose_photo()

        if not file_path:
            print("\nPhoto selection cancelled.")
            return

        content = save_photo(file_path, journal_date)

        if content is None:
            return

    elif memory_type == "music":

        content = input("\nEnter music URL: ")

    elif memory_type == "video":

        content = input("\nEnter video URL: ")

    connection = connect_database()

    journal_id = get_or_create_journal(
        connection,
        journal_date
    )

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO memories
        (journal_id, memory_type, content, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            journal_id,
            memory_type,
            content,
            current_time,
            current_time
        )
    )

    update_journal_time(
        connection,
        journal_id
    )

    connection.commit()
    connection.close()

    print("\nMemory saved successfully.")

    if memory_type == "photo":
        print(f"Photo saved to: {content}")


def view_journal():
    journal_date = input("Enter journal date (YYYY-MM-DD): ")

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, memory_type, content, created_at, updated_at
        FROM memories
        WHERE journal_id = (
            SELECT id
            FROM journals
            WHERE journal_date = ?
        )
        ORDER BY created_at
        """,
        (journal_date,)
    )

    memories = cursor.fetchall()

    connection.close()

    if not memories:
        print("\nNo memories found for this date.")
        return

    print(f"\n===== JOURNAL: {journal_date} =====")

    for memory in memories:

        memory_id, memory_type, content, created_at, updated_at = memory

        print(f"\nMemory ID: {memory_id}")
        print(f"Type: {memory_type}")
        print(f"Created: {created_at}")
        print(f"Updated: {updated_at}")
        print(f"Content: {content}")


def edit_memory():

    journal_date = input("Enter journal date (YYYY-MM-DD): ")

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, memory_type, content, created_at, updated_at
        FROM memories
        WHERE journal_id = (
            SELECT id
            FROM journals
            WHERE journal_date = ?
        )
        ORDER BY created_at
        """,
        (journal_date,)
    )

    memories = cursor.fetchall()

    if not memories:

        print("\nNo memories found for this date.")

        connection.close()

        return

    print(
        f"\n===== MEMORIES ON {journal_date} ====="
    )

    for memory in memories:

        memory_id, memory_type, content, created_at, updated_at = memory

        print(f"\nMemory ID: {memory_id}")
        print(f"Type: {memory_type}")
        print(f"Content: {content}")
        print(f"Created: {created_at}")
        print(f"Updated: {updated_at}")

    try:

        memory_id = int(
            input(
                "\nEnter the Memory ID you want to edit: "
            )
        )

    except ValueError:

        print("\nInvalid Memory ID.")

        connection.close()

        return

    cursor.execute(
        """
        SELECT content, memory_type, journal_id
        FROM memories
        WHERE id = ?
        """,
        (memory_id,)
    )

    memory = cursor.fetchone()

    if not memory:

        print("\nMemory not found.")

        connection.close()

        return

    old_content, memory_type, journal_id = memory

    print("\nCurrent content:")
    print(old_content)

    if memory_type == "photo":

        print("\nChoose a replacement photo.")

        file_path = choose_photo()

        if not file_path:

            print("\nPhoto selection cancelled.")

            connection.close()

            return

        new_content = save_photo(
            file_path,
            journal_date
        )

        if new_content is None:

            connection.close()

            return

    elif memory_type == "text":

        new_content = input(
            "\nEnter new content: "
        )

    elif memory_type == "music":

        new_content = input(
            "\nEnter new music URL: "
        )

    elif memory_type == "video":

        new_content = input(
            "\nEnter new video URL: "
        )

    else:

        print("\nUnsupported memory type.")

        connection.close()

        return

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute(
        """
        UPDATE memories
        SET content = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            new_content,
            current_time,
            memory_id
        )
    )

    update_journal_time(
        connection,
        journal_id
    )

    connection.commit()
    connection.close()

    print("\nMemory updated successfully.")


def delete_memory():

    journal_date = input("Enter journal date (YYYY-MM-DD): ")

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, memory_type, content, created_at
        FROM memories
        WHERE journal_id = (
            SELECT id
            FROM journals
            WHERE journal_date = ?
        )
        ORDER BY created_at
        """,
        (journal_date,)
    )

    memories = cursor.fetchall()

    if not memories:

        print("\nNo memories found for this date.")

        connection.close()

        return

    print(
        f"\n===== MEMORIES ON {journal_date} ====="
    )

    for memory in memories:

        memory_id, memory_type, content, created_at = memory

        print(f"\nMemory ID: {memory_id}")
        print(f"Type: {memory_type}")
        print(f"Content: {content}")
        print(f"Created: {created_at}")

    try:

        memory_id = int(
            input(
                "\nEnter the Memory ID you want to delete: "
            )
        )

    except ValueError:

        print("\nInvalid Memory ID.")

        connection.close()

        return

    cursor.execute(
        """
        SELECT journal_id, content
        FROM memories
        WHERE id = ?
        """,
        (memory_id,)
    )

    memory = cursor.fetchone()

    if not memory:

        print("\nMemory not found.")

        connection.close()

        return

    journal_id, content = memory

    print("\nMemory to delete:")
    print(content)

    confirmation = input(
        "\nAre you sure you want to delete this memory? (y/n): "
    ).lower()

    if confirmation != "y":

        print("\nDeletion cancelled.")

        connection.close()

        return

    cursor.execute(
        """
        DELETE FROM memories
        WHERE id = ?
        """,
        (memory_id,)
    )

    update_journal_time(
        connection,
        journal_id
    )

    connection.commit()
    connection.close()

    print("\nMemory deleted successfully.")


def main():

    while True:

        print("\n===== MEMENTO AI =====")
        print("1. Add a memory")
        print("2. View a journal")
        print("3. Edit a memory")
        print("4. Delete a memory")
        print("5. Exit")

        choice = input(
            "\nChoose an option: "
        )

        if choice == "1":

            add_memory()

        elif choice == "2":

            view_journal()

        elif choice == "3":

            edit_memory()

        elif choice == "4":

            delete_memory()

        elif choice == "5":

            print("\nGoodbye!")

            break

        else:

            print(
                "\nInvalid choice. Please try again."
            )


if __name__ == "__main__":

    main()