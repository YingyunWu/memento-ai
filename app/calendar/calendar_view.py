import calendar

from app.calendar.calendar_service import (
    build_month_calendar,
)


# ============================================================
# Formatting
# ============================================================

def format_keyword(keyword, max_length=12):
    """
    Format a keyword for terminal display.

    Long user-defined keywords are shortened only
    for display. The original keyword in the database
    is never modified.
    """

    if not keyword:
        return ""

    keyword = str(keyword).strip()

    if len(keyword) <= max_length:
        return keyword

    return keyword[:max_length - 1] + "…"


# ============================================================
# Render monthly calendar
# ============================================================

def render_month_calendar(year, month):
    """
    Render a monthly keyword calendar in the terminal.

    The database content is never modified.
    """

    calendar_data = build_month_calendar(
        year,
        month,
    )

    weeks = calendar_data["weeks"]
    days = calendar_data["days"]

    day_map = {
        item["day"]: item
        for item in days
    }

    print()

    print(
        f"===== {calendar_data['month_name'].upper()} "
        f"{year} ====="
    )

    print()

    print(
        "Mon      Tue      Wed      Thu      "
        "Fri      Sat      Sun"
    )

    print(
        "-" * 65
    )

    for week in weeks:

        day_line = ""

        keyword_line = ""

        for day_number in week:

            if day_number == 0:

                day_line += (
                    "         "
                )

                keyword_line += (
                    "         "
                )

                continue

            day_line += (
                f"{day_number:<9}"
            )

            item = day_map.get(
                day_number
            )

            if item and item["has_keyword"]:

                keyword = format_keyword(
                    item["keyword"]
                )

                keyword_line += (
                    f"{keyword:<9}"
                )

            else:

                keyword_line += (
                    f"{'·':<9}"
                )

        print(
            day_line.rstrip()
        )

        print(
            keyword_line.rstrip()
        )

        print()


# ============================================================
# Calendar summary
# ============================================================

def render_calendar_summary(
    year,
    month,
):
    """
    Print a compact monthly summary.
    """

    calendar_data = build_month_calendar(
        year,
        month,
    )

    days = calendar_data["days"]

    keyword_days = [
        day
        for day in days
        if day["has_keyword"]
    ]

    print(
        f"Keyword days: "
        f"{len(keyword_days)}/{len(days)}"
    )

    if keyword_days:

        print(
            "\nHighlights:"
        )

        for item in keyword_days:

            source = (
                item["keyword_source"]
                or "unknown"
            )

            print(
                f"{item['date']}  "
                f"{item['keyword']} "
                f"({source})"
            )


# ============================================================
# Full calendar view
# ============================================================

def show_month_calendar(
    year,
    month,
):
    """
    Display the monthly keyword calendar.
    """

    render_month_calendar(
        year,
        month,
    )

    print()

    render_calendar_summary(
        year,
        month,
    )

    print(
        "\n=============================="
    )
