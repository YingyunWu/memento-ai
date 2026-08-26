from datetime import datetime


from app.database.database import (
    initialize_database,
)


from app.memory.memory_service import (
    add_memory,
    get_memory,
    get_memories,
    update_memory,
    delete_memory,
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


from app.keyword.keyword_service import (
    generate_daily_keyword_candidates,
    get_daily_keyword,
    get_monthly_keywords,
    set_final_keyword,
)


from app.calendar.calendar_view import (
    show_month_calendar,
)


# ============================================================
# Header
# ============================================================

def print_header():

    print("\n===== MEMENTO AI =====")


# ============================================================
# Journal date
# ============================================================

def get_journal_date():

    while True:

        journal_date = input(
            "Enter journal date (YYYY-MM-DD): "
        ).strip()

        try:

            datetime.strptime(
                journal_date,
                "%Y-%m-%d",
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

    if not analyses:

        print(
            "\nNo AI analysis found."
        )

        return

    print(
        "\n===== AI ANALYSIS ====="
    )

    for analysis in analyses:

        analysis_type = analysis.get(
            "analysis_type",
            "unknown",
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
                "Unknown"
            )

            reason = analysis.get(
                "reason"
            )

            if reason:

                print(
                    f"Reason: {reason}"
                )

            continue

        if isinstance(
            result,
            list,
        ):

            for item in result:

                print(
                    f"- {item}"
                )

        elif isinstance(
            result,
            dict,
        ):

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
# Add Text
# ============================================================

def add_text_memory():

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

        memory = add_memory(
            journal_date=journal_date,
            memory_type="text",
            content=content,
            source_type="text",
        )

    except Exception as error:

        print(
            f"Could not save memory: {error}"
        )

        return

    print(
        f"\nText memory saved successfully. "
        f"Memory ID: {memory['id']}"
    )

    analyze = input(
        "\nAnalyze this memory with AI? (y/n): "
    ).strip().lower()

    if analyze != "y":

        return

    print(
        "\nAnalyzing memory with AI..."
    )

    try:

        analyses = analyze_and_store_text_memory(
            memory["id"],
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
# Add Photo
# ============================================================

def add_photo_memory():

    journal_date = get_journal_date()

    print(
        "\nChoose photo files."
    )

    try:

        file_paths = choose_photo_files()

    except Exception as error:

        print(
            f"Could not choose photo: {error}"
        )

        return

    if not file_paths:

        print(
            "No photo selected."
        )

        return

    try:

        saved_files = save_photo(
            file_paths,
            journal_date,
        )

    except Exception as error:

        print(
            f"Could not save photo: {error}"
        )

        return

    if isinstance(
        saved_files,
        str,
    ):

        saved_files = [
            saved_files
        ]

    for file_path in saved_files:

        try:

            memory = add_memory(
                journal_date=journal_date,
                memory_type="photo",
                content=file_path,
                source_type="photo",
                file_path=file_path,
            )

            print(
                f"\nPhoto memory saved successfully. "
                f"Memory ID: {memory['id']}"
            )

        except Exception as error:

            print(
                f"Could not save photo memory: {error}"
            )


# ============================================================
# Add Music
# ============================================================

def add_music_memory():

    journal_date = get_journal_date()

    url = input(
        "Enter music URL: "
    ).strip()

    if not url:

        print(
            "Music URL cannot be empty."
        )

        return

    try:

        valid = validate_music_url(
            url
        )

    except Exception as error:

        print(
            f"Invalid music URL: {error}"
        )

        return

    if valid is False:

        print(
            "Invalid music URL."
        )

        return

    try:

        memory = add_memory(
            journal_date=journal_date,
            memory_type="music",
            content=url,
            source_type="music",
            file_path=None,
            platform="url",
        )

        print(
            f"\nMusic memory saved successfully. "
            f"Memory ID: {memory['id']}"
        )

    except Exception as error:

        print(
            f"Could not save music memory: {error}"
        )


# ============================================================
# Add Video
# ============================================================

def add_video_memory():

    journal_date = get_journal_date()

    url = input(
        "Enter video URL: "
    ).strip()

    if not url:

        print(
            "Video URL cannot be empty."
        )

        return

    try:

        valid = validate_video_url(
            url
        )

    except Exception as error:

        print(
            f"Invalid video URL: {error}"
        )

        return

    if valid is False:

        print(
            "Invalid video URL."
        )

        return

    try:

        memory = add_memory(
            journal_date=journal_date,
            memory_type="video",
            content=url,
            source_type="video",
            file_path=None,
            platform="url",
        )

        print(
            f"\nVideo memory saved successfully. "
            f"Memory ID: {memory['id']}"
        )

    except Exception as error:

        print(
            f"Could not save video memory: {error}"
        )


# ============================================================
# View Journal
# ============================================================

def view_journal():

    journal_date = get_journal_date()

    try:

        memories = get_memories(
            journal_date
        )

    except Exception as error:

        print(
            f"Could not load journal: {error}"
        )

        return

    print(
        f"\n===== JOURNAL: {journal_date} ====="
    )

    if not memories:

        print(
            "No memories found."
        )

        return

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

        if memory.get(
            "platform"
        ):

            print(
                f"Platform: {memory['platform']}"
            )

        if memory.get(
            "file_path"
        ):

            print(
                f"File: {memory['file_path']}"
            )

        print(
            f"Created: {memory['created_at']}"
        )

    print(
        "\n================================"
    )


# ============================================================
# View AI Analysis
# ============================================================

def view_ai_analysis():

    journal_date = get_journal_date()

    try:

        memories = get_memories(
            journal_date
        )

    except Exception as error:

        print(
            f"Could not load journal: {error}"
        )

        return

    if not memories:

        print(
            "\nNo memories found for this date."
        )

        return

    found = False

    for memory in memories:

        try:

            analyses = get_memory_analyses(
                memory["id"]
            )

        except Exception as error:

            print(
                f"Could not load analysis "
                f"for memory {memory['id']}: "
                f"{error}"
            )

            continue

        if not analyses:

            continue

        found = True

        print(
            f"\n===== MEMORY {memory['id']} ====="
        )

        print(
            f"Type: {memory['memory_type']}"
        )

        print(
            f"Content: {memory['content']}"
        )

        display_ai_analysis(
            analyses
        )

    if not found:

        print(
            "\nNo AI analysis found."
        )


# ============================================================
# Daily Keyword
# ============================================================

def daily_keyword():

    journal_date = get_journal_date()

    try:

        memories = get_memories(
            journal_date
        )

    except Exception as error:

        print(
            f"Could not load memories: {error}"
        )

        return

    if not memories:

        print(
            "\nNo memories found for this date."
        )

        print(
            "Add some memories first."
        )

        return

    print(
        "\n===== DAILY KEYWORD ====="
    )

    try:

        existing = get_daily_keyword(
            journal_date
        )

    except Exception as error:

        print(
            f"Could not load daily keyword: {error}"
        )

        existing = None

    if existing:

        final_keyword = existing.get(
            "final_keyword"
        )

        if final_keyword:

            print(
                f"\nCurrent keyword: "
                f"{final_keyword}"
            )

            print(
                f"Source: "
                f"{existing.get('keyword_source')}"
            )

    print(
        "\nGenerating AI keyword candidates..."
    )

    try:

        candidates = (
            generate_daily_keyword_candidates(
                journal_date
            )
        )

    except Exception as error:

        print(
            f"\nAI keyword generation failed: {error}"
        )

        return

    if not candidates:

        print(
            "\nAI could not determine "
            "a reliable keyword."
        )

        return

    print(
        "\nAI candidates:"
    )

    for index, candidate in enumerate(
        candidates,
        start=1,
    ):

        print(
            f"{index}. {candidate}"
        )

    print(
        "\nYou can choose an AI keyword "
        "or write your own."
    )

    choice = input(
        "\nEnter the number, "
        "or press Enter for your own: "
    ).strip()

    selected_keyword = None
    source = "user"

    if choice.isdigit():

        index = int(
            choice
        ) - 1

        if (
            0 <= index < len(candidates)
        ):

            selected_keyword = (
                candidates[index]
            )

            source = "ai"

    if selected_keyword is None:

        selected_keyword = input(
            "\nEnter your own keyword: "
        ).strip()

        if not selected_keyword:

            print(
                "Keyword cannot be empty."
            )

            return

        source = "user"

    try:

        set_final_keyword(
            journal_date,
            selected_keyword,
            source,
        )

    except Exception as error:

        print(
            f"\nCould not save keyword: {error}"
        )

        return

    print(
        "\n===== DAILY KEYWORD ====="
    )

    print(
        f"Date: {journal_date}"
    )

    print(
        f"Keyword: {selected_keyword}"
    )

    print(
        f"Source: {source}"
    )

    print(
        "========================="
    )


# ============================================================
# Monthly Memory Calendar
# ============================================================

def view_monthly_calendar():

    print(
        "\n===== MONTHLY MEMORY CALENDAR ====="
    )

    while True:

        year_input = input(
            "Enter year (YYYY): "
        ).strip()

        try:

            year = int(
                year_input
            )

        except ValueError:

            print(
                "Invalid year."
            )

            continue

        if year < 1:

            print(
                "Invalid year."
            )

            continue

        break

    while True:

        month_input = input(
            "Enter month (1-12): "
        ).strip()

        try:

            month = int(
                month_input
            )

        except ValueError:

            print(
                "Invalid month."
            )

            continue

        if not 1 <= month <= 12:

            print(
                "Invalid month."
            )

            continue

        break

    try:

        show_month_calendar(
            year,
            month,
        )

    except Exception as error:

        print(
            f"\nUnable to display calendar: "
            f"{error}"
        )


# ============================================================
# Edit Memory
# ============================================================

def edit_existing_memory():

    try:

        memory_id = int(
            input(
                "Enter memory ID to edit: "
            ).strip()
        )

    except ValueError:

        print(
            "Invalid memory ID."
        )

        return

    try:

        memory = get_memory(
            memory_id
        )

    except Exception as error:

        print(
            f"Could not load memory: {error}"
        )

        return

    if memory is None:

        print(
            "Memory not found."
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

        result = update_memory(
            memory_id,
            new_content=new_content,
        )

    except Exception as error:

        print(
            f"Could not update memory: {error}"
        )

        return

    if result:

        print(
            "Memory updated successfully."
        )

    else:

        print(
            "Memory was not updated."
        )


# ============================================================
# Delete Memory
# ============================================================

def delete_existing_memory():

    try:

        memory_id = int(
            input(
                "Enter memory ID to delete: "
            ).strip()
        )

    except ValueError:

        print(
            "Invalid memory ID."
        )

        return

    try:

        memory = get_memory(
            memory_id
        )

    except Exception as error:

        print(
            f"Could not load memory: {error}"
        )

        return

    if memory is None:

        print(
            "Memory not found."
        )

        return

    print(
        f"\nMemory ID: {memory['id']}"
    )

    print(
        f"Type: {memory['memory_type']}"
    )

    print(
        f"Content: {memory['content']}"
    )

    confirm = input(
        "\nAre you sure you want to delete "
        "this memory? (y/n): "
    ).strip().lower()

    if confirm != "y":

        print(
            "Deletion cancelled."
        )

        return

    try:

        result = delete_memory(
            memory_id
        )

    except Exception as error:

        print(
            f"Could not delete memory: {error}"
        )

        return

    if result:

        print(
            "Memory deleted successfully."
        )

    else:

        print(
            "Memory was not deleted."
        )


# ============================================================
# Show Memory Types
# ============================================================

def show_memory_types():

    try:

        memory_types = (
            get_supported_memory_types()
        )

    except Exception as error:

        print(
            f"Could not load memory types: {error}"
        )

        return

    print(
        "\n===== MEMORY TYPES ====="
    )

    for memory_type in memory_types:

        print(
            f"- {memory_type}"
        )

    print(
        "========================"
    )


# ============================================================
# Main
# ============================================================

def main():

    initialize_database()

    while True:

        print_header()

        print(
            "1. Add Text"
        )

        print(
            "2. Add Photo"
        )

        print(
            "3. Add Music"
        )

        print(
            "4. Add Video"
        )

        print(
            "5. View Journal"
        )

        print(
            "6. View AI Analysis"
        )

        print(
            "7. Daily Keyword"
        )

        print(
            "8. Monthly Memory Calendar"
        )

        print(
            "9. Edit Memory"
        )

        print(
            "10. Delete Memory"
        )

        print(
            "11. Show Memory Types"
        )

        print(
            "12. Exit"
        )

        choice = input(
            "\nChoose an option: "
        ).strip()

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

            daily_keyword()

        elif choice == "8":

            view_monthly_calendar()

        elif choice == "9":

            edit_existing_memory()

        elif choice == "10":

            delete_existing_memory()

        elif choice == "11":

            show_memory_types()

        elif choice == "12":

            print(
                "\nGoodbye."
            )

            break

        else:

            print(
                "\nInvalid option."
            )


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":

    main()