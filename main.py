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

from app.analysis.analysis_service import (
    analyze_and_store_text_memory,
    get_memory_analyses,
)

from app.media.media_service import (
    choose_photo_files,
    save_photo,
    validate_music_url,
    validate_video_url,
)


# ============================================================
# UI helpers
# ============================================================

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


# ============================================================
# Display AI analysis
# ============================================================

def display_ai_analysis(analyses):
    """
    Display stored AI analysis results.
    """

    if not analyses:

        print(
            "\nNo AI analysis results found."
        )

        return

    print(
        "\n===== AI ANALYSIS ====="
    )

    for analysis in analyses:

        analysis_type = analysis.get(
            "analysis_type"
        )

        result = analysis.get(
            "result"
        )

        status = analysis.get(
            "status"
        )

        print(
            f"\n{analysis_type.capitalize()}:"
        )

        if status == "unknown":

            print(
                "Unable to determine reliably."
            )

            reason = analysis.get(
                "reason"
            )

            if reason:

                print(
                    f"Reason: {reason}"
                )

        elif status == "failed":

            print(
                "Analysis failed."
            )

            reason = analysis.get(
                "reason"
            )

            if reason:

                print(
                    f"Reason: {reason}"
                )

        else:

            if isinstance(result, list):

                for item in result:

                    print(
                        f"- {item}"
                    )

            elif isinstance(result, dict):

                for key, value in result.items():

                    print(
                        f"{key}: {value}"
                    )

            else:

                print(
                    result
                )

    print(
        "\n======================="
    )


# ============================================================
# Add Text Memory
# ============================================================

def add_text_memory():
    """
    Add a text memory and optionally analyze it with AI.
    """

    journal_date = get_journal_date()

    content = input(
        "What would you like to remember? "
    ).strip()

    if not content:

        print(
            "Memory cannot be empty."
        )

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

        print(
            f"Error: {error}"
        )

        return

    # --------------------------------------------------------
    # Optional AI analysis
    # --------------------------------------------------------

    analyze_choice = input(
        "\nAnalyze this memory with AI? (y/n): "
    ).strip().lower()

    if analyze_choice != "y":

        return

    try:

        print(
            "\nAnalyzing memory with AI..."
        )

        analyses = analyze_and_store_text_memory(
            memory_id,
            content,
        )

        display_ai_analysis(
            analyses
        )

    except Exception as error:

        print(
            f"\nAI analysis failed: {error}"
        )


# ============================================================
# Add Photo Memory
# ============================================================

def add_photo_memory():
    """
    Add one or more photo memories.

    The photo picker may return multiple files.
    Each selected photo is stored as a separate
    memory record.
    """

    journal_date = get_journal_date()

    print(
        "\nOpening photo picker..."
    )

    file_paths = choose_photo_files()

    if not file_paths:

        print(
            "No photos selected. "
            "Photo memory cancelled."
        )

        return

    try:

        saved_paths = save_photo(
            file_paths,
            journal_date
        )

        if not isinstance(
            saved_paths,
            list
        ):

            saved_paths = [
                saved_paths
            ]

        print(
            f"\n{len(saved_paths)} "
            f"photo(s) saved successfully."
        )

        for stored_path in saved_paths:

            memory_id = create_memory(
                journal_date,
                "photo",
                stored_path
            )

            print(
                f"\nMemory ID: {memory_id}"
            )

            print(
                f"Photo: {stored_path}"
            )

    except (
        FileNotFoundError,
        ValueError
    ) as error:

        print(
            f"Error: {error}"
        )


# ============================================================
# Add Music Memory
# ============================================================

def add_music_memory():
    """
    Add a music memory using a URL.
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

        print(
            f"Error: {error}"
        )


# ============================================================
# Add Video Memory
# ============================================================

def add_video_memory():
    """
    Add a video memory using a URL.
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

        print(
            f"Error: {error}"
        )


# ============================================================
# View Journal
# ============================================================

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

        print(
            "No memories found for this date."
        )

        return

    for memory in memories:

        print(
            "\n------------------------------"
        )

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

        if memory.get("file_path"):

            print(
                f"File: {memory['file_path']}"
            )

        if memory.get("platform"):

            print(
                f"Platform: {memory['platform']}"
            )

        # ----------------------------------------------------
        # Show AI analysis
        # ----------------------------------------------------

        if memory["memory_type"] == "text":

            try:

                analyses = get_memory_analyses(
                    memory["id"]
                )

                if analyses:

                    print(
                        "\nAI Analysis:"
                    )

                    for analysis in analyses:

                        analysis_type = analysis.get(
                            "analysis_type"
                        )

                        status = analysis.get(
                            "status"
                        )

                        result = analysis.get(
                            "result"
                        )

                        print(
                            f"- {analysis_type}: ",
                            end=""
                        )

                        if status == "unknown":

                            print(
                                "unknown"
                            )

                        elif isinstance(
                            result,
                            list
                        ):

                            print(
                                ", ".join(
                                    str(item)
                                    for item in result
                                )
                            )

                        else:

                            print(
                                result
                            )

            except Exception:

                pass

    print(
        "\n------------------------------"
    )


# ============================================================
# View AI Analysis
# ============================================================

def view_ai_analysis():
    """
    Display AI analysis for a specific memory.
    """

    try:

        memory_id = int(
            input(
                "\nEnter Memory ID: "
            )
        )

    except ValueError:

        print(
            "Invalid Memory ID."
        )

        return

    memory = get_single_memory(
        memory_id
    )

    if not memory:

        print(
            "Memory not found."
        )

        return

    try:

        analyses = get_memory_analyses(
            memory_id
        )

        print(
            f"\n===== AI ANALYSIS "
            f"FOR MEMORY {memory_id} ====="
        )

        display_ai_analysis(
            analyses
        )

    except Exception as error:

        print(
            f"Could not load AI analysis: {error}"
        )


# ============================================================
# Edit Memory
# ============================================================

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

        print(
            "Invalid Memory ID."
        )

        return

    memory = get_single_memory(
        memory_id
    )

    if not memory:

        print(
            "Memory not found."
        )

        return

    if memory["journal_date"] != journal_date:

        print(
            "This memory does not belong "
            "to the selected journal."
        )

        return

    print(
        "\nCurrent content:"
    )

    print(
        memory["content"]
    )

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

        print(
            f"Error: {error}"
        )


# ============================================================
# Delete Memory
# ============================================================

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

        print(
            "Invalid Memory ID."
        )

        return

    memory = get_single_memory(
        memory_id
    )

    if not memory:

        print(
            "Memory not found."
        )

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

        print(
            "Deletion cancelled."
        )

        return

    try:

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

    except ValueError as error:

        print(
            f"Error: {error}"
        )


# ============================================================
# Show supported memory types
# ============================================================

def show_memory_types():
    """
    Display supported memory types.
    """

    print(
        "\nSupported memory types:"
    )

    for memory_type in get_supported_memory_types():

        print(
            f"- {memory_type.capitalize()}"
        )


# ============================================================
# Main application
# ============================================================

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
        print("6. View AI Analysis")
        print("7. Edit Memory")
        print("8. Delete Memory")
        print("9. Show Memory Types")
        print("10. Exit")

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

            view_ai_analysis()

        elif choice == "7":

            edit_existing_memory()

        elif choice == "8":

            delete_existing_memory()

        elif choice == "9":

            show_memory_types()

        elif choice == "10":

            print(
                "\nThank you for using Memento AI."
            )

            break

        else:

            print(
                "\nInvalid option. "
                "Please choose 1-10."
            )


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    main()