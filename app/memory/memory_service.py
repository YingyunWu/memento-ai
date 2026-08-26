from app.database.database import (
    add_memory,
    get_memories,
    get_memory,
    update_memory,
    delete_memory,
)


# ============================================================
# Supported memory types
# ============================================================

MEMORY_TYPES = {
    "text",
    "photo",
    "music",
    "video",
}


# ============================================================
# Supported source types
# ============================================================

SOURCE_TYPES = {
    "text",
    "upload",
    "url",
}


# ============================================================
# Supported platforms
# ============================================================

SUPPORTED_PLATFORMS = {
    "qq_music",
    "netease_cloud_music",
    "apple_music",
    "youtube",
    "douyin",
    "bilibili",
    "other",
}


# ============================================================
# Automatic AI keyword update
# ============================================================

def _refresh_ai_keyword_if_needed(
    journal_date,
):
    """
    Refresh the daily AI keyword when appropriate.

    Rules:

        1. No existing keyword:
           Generate an AI keyword.

        2. Existing keyword_source == "ai":
           Regenerate the AI keyword because the day's
           memories have changed.

        3. Existing keyword_source == "user":
           Keep the user's keyword unchanged.

    AI errors are intentionally caught so that a failure
    in DeepSeek never prevents the memory itself from
    being saved.
    """

    try:

        from app.keyword.keyword_service import (
            get_daily_keyword,
            generate_daily_keyword_candidates,
        )

        keyword = get_daily_keyword(
            journal_date
        )

        # ----------------------------------------------------
        # No keyword yet
        # ----------------------------------------------------

        if keyword is None:

            generate_daily_keyword_candidates(
                journal_date
            )

            return

        # ----------------------------------------------------
        # AI-owned keyword
        # ----------------------------------------------------

        keyword_source = keyword.get(
            "keyword_source"
        )

        if keyword_source == "ai":

            generate_daily_keyword_candidates(
                journal_date
            )

            return

        # ----------------------------------------------------
        # User-owned keyword
        # ----------------------------------------------------

        if keyword_source == "user":

            return

        # ----------------------------------------------------
        # Existing record but no final keyword/source
        # ----------------------------------------------------

        final_keyword = keyword.get(
            "final_keyword"
        )

        if not final_keyword:

            generate_daily_keyword_candidates(
                journal_date
            )

    except Exception as error:

        print(
            "AI keyword update failed: "
            f"{error}"
        )


# ============================================================
# Create memory
# ============================================================

def create_memory(
    journal_date,
    memory_type,
    content="",
    source_type=None,
    file_path=None,
    platform=None,
):
    """
    Create a new memory for a specific journal date.

    Supported memory types:
        text
        photo
        music
        video

    Supported source types:
        text
        upload
        url
    """

    # --------------------------------------------------------
    # Normalize memory type
    # --------------------------------------------------------

    memory_type = memory_type.lower().strip()

    if memory_type not in MEMORY_TYPES:

        raise ValueError(
            f"Unsupported memory type: {memory_type}. "
            f"Supported types are: "
            f"{', '.join(sorted(MEMORY_TYPES))}"
        )

    # --------------------------------------------------------
    # Automatically determine source type
    # --------------------------------------------------------

    if source_type is None:

        if file_path:

            source_type = "upload"

        elif content:

            source_type = "text"

        else:

            raise ValueError(
                "Memory must contain content or a file."
            )

    source_type = source_type.lower().strip()

    if source_type not in SOURCE_TYPES:

        raise ValueError(
            f"Unsupported source type: {source_type}. "
            f"Supported types are: "
            f"{', '.join(sorted(SOURCE_TYPES))}"
        )

    # --------------------------------------------------------
    # Validate text content
    # --------------------------------------------------------

    if source_type == "text":

        if not content or not content.strip():

            raise ValueError(
                "Memory content cannot be empty."
            )

        content = content.strip()

    # --------------------------------------------------------
    # Validate URL
    # --------------------------------------------------------

    elif source_type == "url":

        if not content or not content.strip():

            raise ValueError(
                "URL cannot be empty."
            )

        content = content.strip()

    # --------------------------------------------------------
    # Validate uploaded file
    # --------------------------------------------------------

    elif source_type == "upload":

        if not file_path:

            raise ValueError(
                "Uploaded memory requires a file path."
            )

        file_path = file_path.strip()

        if not file_path:

            raise ValueError(
                "File path cannot be empty."
            )

        if not content:

            content = ""

    # --------------------------------------------------------
    # Validate platform
    # --------------------------------------------------------

    if platform:

        platform = platform.lower().strip()

        if platform not in SUPPORTED_PLATFORMS:

            raise ValueError(
                f"Unsupported platform: {platform}. "
                f"Supported platforms are: "
                f"{', '.join(sorted(SUPPORTED_PLATFORMS))}"
            )

    # --------------------------------------------------------
    # Save memory first
    # --------------------------------------------------------

    memory_id = add_memory(
        journal_date=journal_date,
        memory_type=memory_type,
        content=content,
        source_type=source_type,
        file_path=file_path,
        platform=platform,
    )

    # --------------------------------------------------------
    # Refresh AI keyword after successful save
    # --------------------------------------------------------

    _refresh_ai_keyword_if_needed(
        journal_date
    )

    return memory_id


# ============================================================
# Get journal memories
# ============================================================

def get_journal_memories(
    journal_date,
):
    """
    Get all memories belonging to a journal day.
    """

    return get_memories(
        journal_date
    )


# ============================================================
# Get single memory
# ============================================================

def get_single_memory(
    memory_id,
):
    """
    Get one memory by ID.
    """

    return get_memory(
        memory_id
    )


# ============================================================
# Edit memory
# ============================================================

def edit_memory(
    memory_id,
    new_content=None,
    new_file_path=None,
    new_platform=None,
):
    """
    Edit an existing memory.

    Text memories:
        update content.

    Uploaded media:
        optionally update file path.

    URL memories:
        optionally update URL.

    Platform can also be updated.

    If the day's keyword is AI-generated,
    the keyword will be regenerated after
    the edit.

    If the day's keyword was manually chosen
    by the user, it will remain unchanged.
    """

    if (
        new_content is None
        and new_file_path is None
        and new_platform is None
    ):

        raise ValueError(
            "Nothing to update."
        )

    # --------------------------------------------------------
    # Get existing memory before editing
    # --------------------------------------------------------

    existing_memory = get_memory(
        memory_id
    )

    if existing_memory is None:

        raise ValueError(
            f"Memory {memory_id} does not exist."
        )

    journal_date = existing_memory[
        "journal_date"
    ]

    # --------------------------------------------------------
    # Validate content
    # --------------------------------------------------------

    if new_content is not None:

        new_content = new_content.strip()

        if not new_content:

            raise ValueError(
                "Memory content cannot be empty."
            )

    # --------------------------------------------------------
    # Validate file path
    # --------------------------------------------------------

    if new_file_path is not None:

        new_file_path = new_file_path.strip()

        if not new_file_path:

            raise ValueError(
                "File path cannot be empty."
            )

    # --------------------------------------------------------
    # Validate platform
    # --------------------------------------------------------

    if new_platform is not None:

        new_platform = (
            new_platform
            .lower()
            .strip()
        )

        if new_platform not in SUPPORTED_PLATFORMS:

            raise ValueError(
                f"Unsupported platform: {new_platform}. "
                f"Supported platforms are: "
                f"{', '.join(sorted(SUPPORTED_PLATFORMS))}"
            )

    # --------------------------------------------------------
    # Update database
    # --------------------------------------------------------

    result = update_memory(
        memory_id=memory_id,
        new_content=new_content,
        new_file_path=new_file_path,
        new_platform=new_platform,
    )

    # --------------------------------------------------------
    # Refresh AI keyword
    # --------------------------------------------------------

    _refresh_ai_keyword_if_needed(
        journal_date
    )

    return result


# ============================================================
# Delete memory
# ============================================================

def remove_memory(
    memory_id,
):
    """
    Delete an existing memory.
    """

    existing_memory = get_memory(
        memory_id
    )

    if existing_memory is None:

        raise ValueError(
            f"Memory {memory_id} does not exist."
        )

    journal_date = existing_memory[
        "journal_date"
    ]

    result = delete_memory(
        memory_id
    )

    # --------------------------------------------------------
    # Deleting a memory also changes the day's content.
    # If the keyword belongs to AI, regenerate it.
    # If the keyword belongs to the user, preserve it.
    # --------------------------------------------------------

    _refresh_ai_keyword_if_needed(
        journal_date
    )

    return result


# ============================================================
# Memory types
# ============================================================

def get_supported_memory_types():
    """
    Return all supported memory types.
    """

    return sorted(
        MEMORY_TYPES
    )


# ============================================================
# Source types
# ============================================================

def get_supported_source_types():
    """
    Return all supported source types.
    """

    return sorted(
        SOURCE_TYPES
    )


# ============================================================
# Platforms
# ============================================================

def get_supported_platforms():
    """
    Return all supported platforms.
    """

    return sorted(
        SUPPORTED_PLATFORMS
    )