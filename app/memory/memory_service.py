from app.database.database import (
    add_memory,
    get_memories,
    get_memory,
    update_memory,
    delete_memory,
)


# Supported memory types
MEMORY_TYPES = {
    "text",
    "photo",
    "music",
    "video",
}


def create_memory(journal_date, memory_type, content):
    """
    Create a new memory for a specific journal date.

    Supported memory types:
        text
        photo
        music
        video
    """

    memory_type = memory_type.lower().strip()

    if memory_type not in MEMORY_TYPES:
        raise ValueError(
            f"Unsupported memory type: {memory_type}. "
            f"Supported types are: {', '.join(sorted(MEMORY_TYPES))}"
        )

    if not content or not content.strip():
        raise ValueError("Memory content cannot be empty.")

    return add_memory(
        journal_date=journal_date,
        memory_type=memory_type,
        content=content.strip(),
    )


def get_journal_memories(journal_date):
    """
    Get all memories for a specific journal date.
    """
    return get_memories(journal_date)


def get_single_memory(memory_id):
    """
    Get one memory by ID.
    """
    return get_memory(memory_id)


def edit_memory(memory_id, new_content):
    """
    Edit an existing memory.
    """
    if not new_content or not new_content.strip():
        raise ValueError("Memory content cannot be empty.")

    return update_memory(
        memory_id=memory_id,
        new_content=new_content.strip(),
    )


def remove_memory(memory_id):
    """
    Delete an existing memory.
    """
    return delete_memory(memory_id)


def get_supported_memory_types():
    """
    Return all supported memory types.
    """
    return sorted(MEMORY_TYPES)