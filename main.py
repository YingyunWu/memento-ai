from datetime import datetime

from app.database.database import initialize_database
from app.memory.memory_service import (
    create_memory,
    get_journal_memories,
    get_single_memory,
    edit_memory,
    remove_memory,
    get_supported_memory_types,
)
from app.media.media_service import (
    save_photo,
    validate_music_url,
    validate_video_url,
)


def print_header():
    print("\n===== MEMENTO AI =====")


def get_journal_date():
    """
    Ask the user for a journal date.
    """

    while True:
        journal_date = input(
            "Enter journal date (YYYY-MM-DD): "
        ).strip()

        try:
            datetime.strptime(
                journal_date,
                "%Y-%m-%d"
            )

            return journal_date

        except ValueError:
            print(
                "Invalid date format. "
                "Please use YYYY-MM-DD."
            )


def add_text_memory():
    """
    Add a text memory.
    """

    journal_date = get_journal_date()

    content = input(
        "What would you like to remember? "
    ).strip()

    if not content:
        print("Memory cannot be empty.")
        return

    try:
        memory_id = create_memory(
            journal_date,
            "text",
            content
        )

        print(
            f"\nText memory saved successfully. "
            f"Memory ID: {memory_id}"
        )

    except ValueError as error:
        print(f"Error: {error}")


def add_photo_memory():
    """
    Add a photo memory.
    """

    journal_date = get_journal_date()

    photo_path = input(
        "Enter the path to the photo: "
    ).strip()

    try:
        stored_path = save_photo(
            photo_path,
            journal_date
        )

        memory_id = create_memory(
            journal_date,
            "photo",
            stored_path
        )

        print(
            "\nPhoto memory saved successfully."
        )

        print(
            f"Memory ID: {memory_id}"
        )

        print(
            f"Stored at: {stored_path}"
        )

    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")


def add_music_memory():
    """
    Add a music URL memory.
    """

    journal_date = get_journal_date()

    music_url = input(
        "Enter the music URL: "
    ).strip()

    try:
        music_url = validate_music_url(
            music_url
        )

        memory_id = create_memory(
            journal_date,
            "music",
            music_url
        )

        print(
            f"\nMusic memory saved successfully. "
            f"Memory ID: {memory_id}"
        )

    except ValueError as error:
        print(f"Error: {error}")


def add_video_memory():
    """
    Add a video URL memory.
    """

    journal_date = get_journal_date()

    video_url = input(
        "Enter the video URL: "
    ).strip()

    try:
        video_url = validate_video_url(
            video_url
        )

        memory_id = create_memory(
            journal_date,
            "video",
            video_url
        )

        print(
            f"\nVideo memory saved successfully. "
            f"Memory ID: {memory_id}"
        )

    except ValueError as error:
        print(f"Error: {error}")


def view_journal():
    """
    Display all memories for a specific date.
    """

    journal_date = get_journal_date()

    memories = get_journal_memories(
        journal_date
    )

    print(
        f"\n===== JOURNAL: {journal_date} ====="
    )

    if not memories:
        print("No memories found for this date.")
        return

    for memory in memories:
        print("\n------------------------------")

        print(
            f"Memory ID: {memory['id']}"
        )

        print(
            f"Type: {memory['memory_type']}"
        )

        print(
            f"Created: {memory['created_at']}"
        )

        print(
            f"Updated: {memory['updated_at']}"
        )

        print(
            f"Content: {memory['content']}"
        )

    print("\n------------------------------")


def edit_existing_memory():
    """
    Edit an existing memory.
    """

    journal_date = get_journal_date()

    memories = get_journal_memories(
        journal_date
    )

    if not memories:
        print(
            "No memories found for this date."
        )
        return

    print(
        f"\n===== MEMORIES ON {journal_date} ====="
    )

    for memory in memories:
        print(
            f"\nMemory ID: {memory['id']}"
        )

        print(
            f"Type: {memory['memory_type']}"
        )

        print(
            f"Content: {memory['content']}"
        )

        print(
            f"Created: {memory['created_at']}"
        )

        print(
            f"Updated: {memory['updated_at']}"
        )

    try:
        memory_id = int(
            input(
                "\nEnter the Memory ID "
                "you want to edit: "
            )
        )

    except ValueError:
        print("Invalid Memory ID.")
        return

    memory = get_single_memory(
        memory_id
    )

    if not memory:
        print("Memory not found.")
        return

    if memory["journal_date"] != journal_date:
        print(
            "This memory does not belong "
            "to the selected journal."
        )
        return

    print("\nCurrent content:")
    print(memory["content"])

    new_content = input(
        "\nEnter new content: "
    ).strip()

    if not new_content:
        print(
            "Content cannot be empty."
        )
        return

    try:
        success = edit_memory(
            memory_id,
            new_content
        )

        if success:
            print(
                "\nMemory updated successfully."
            )
        else:
            print(
                "\nMemory could not be updated."
            )

    except ValueError as error:
        print(f"Error: {error}")


def delete_existing_memory():
    """
    Delete an existing memory.
    """

    journal_date = get_journal_date()

    memories = get_journal_memories(
        journal_date
    )

    if not memories:
        print(
            "No memories found for this date."
        )
        return

    print(
        f"\n===== MEMORIES ON {journal_date} ====="
    )

    for memory in memories:
        print(
            f"\nMemory ID: {memory['id']}"
        )

        print(
            f"Type: {memory['memory_type']}"
        )

        print(
            f"Content: {memory['content']}"
        )

    try:
        memory_id = int(
            input(
                "\nEnter the Memory ID "
                "you want to delete: "
            )
        )

    except ValueError:
        print("Invalid Memory ID.")
        return

    memory = get_single_memory(
        memory_id
    )

    if not memory:
        print("Memory not found.")
        return

    if memory["journal_date"] != journal_date:
        print(
            "This memory does not belong "
            "to the selected journal."
        )
        return

    confirmation = input(
        "\nAre you sure you want to delete "
        "this memory? (y/n): "
    ).strip().lower()

    if confirmation != "y":
        print("Deletion cancelled.")
        return

    success = remove_memory(
        memory_id
    )

    if success:
        print(
            "\nMemory deleted successfully."
        )
    else:
        print(
            "\nMemory could not be deleted."
        )


def show_memory_types():
    """
    Display supported memory types.
    """

    print("\nSupported memory types:")

    for memory_type in get_supported_memory_types():
        print(
            f"- {memory_type.capitalize()}"
        )


def main():
    """
    Main application loop.
    """

    initialize_database()

    while True:

        print_header()

        print("1. Add Text")
        print("2. Add Photo")
        print("3. Add Music")
        print("4. Add Video")
        print("5. View Journal")
        print("6. Edit Memory")
        print("7. Delete Memory")
        print("8. Show Memory Types")
        print("9. Exit")

        try:
            choice = input(
                "\nChoose an option: "
            ).strip()

        except KeyboardInterrupt:
            print(
                "\n\nMemento AI closed."
            )
            break

        if choice == "1":
            add_text_memory()

        elif choice == "2":
            add_photo_memory()

        elif choice == "3":
            add_music_memory()

        elif choice == "4":
            add_video_memory()

        elif choice == "5":
            view_journal()

        elif choice == "6":
            edit_existing_memory()

        elif choice == "7":
            delete_existing_memory()

        elif choice == "8":
            show_memory_types()

        elif choice == "9":
            print(
                "\nThank you for using Memento AI."
            )
            break

        else:
            print(
                "\nInvalid option. "
                "Please choose 1-9."
            )


if __name__ == "__main__":
    main()