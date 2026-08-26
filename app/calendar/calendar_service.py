import calendar
from datetime import date

from app.keyword.keyword_service import (
    get_monthly_keywords,
)


# ============================================================
# Calendar data
# ============================================================

def build_month_calendar(year, month):
    """
    Build a calendar representation for Memento AI.

    Each day contains:
        - date
        - day number
        - weekday
        - keyword
        - keyword source
        - whether the day has a keyword
    """

    if not isinstance(year, int):
        raise ValueError(
            "Year must be an integer."
        )

    if not isinstance(month, int):
        raise ValueError(
            "Month must be an integer."
        )

    if not 1 <= month <= 12:
        raise ValueError(
            "Month must be between 1 and 12."
        )

    monthly_keywords = (
        get_monthly_keywords(
            year,
            month,
        )
    )

    keyword_map = {
        item["journal_date"]: item
        for item in monthly_keywords
    }

    month_calendar = []

    _, days_in_month = calendar.monthrange(
        year,
        month,
    )

    for day_number in range(
        1,
        days_in_month + 1,
    ):

        current_date = date(
            year,
            month,
            day_number,
        )

        date_string = (
            current_date.isoformat()
        )

        keyword_data = keyword_map.get(
            date_string
        )

        if keyword_data:

            keyword = keyword_data.get(
                "final_keyword"
            )

            keyword_source = (
                keyword_data.get(
                    "keyword_source"
                )
            )

        else:

            keyword = None
            keyword_source = None

        month_calendar.append(
            {
                "date": date_string,
                "day": day_number,
                "weekday": current_date.weekday(),
                "keyword": keyword,
                "keyword_source": keyword_source,
                "has_keyword": keyword is not None,
            }
        )

    return {
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "weeks": calendar.monthcalendar(
            year,
            month,
        ),
        "days": month_calendar,
    }


# ============================================================
# Calendar summary
# ============================================================

def get_calendar_summary(
    year,
    month,
):
    """
    Return a simple summary of the month's
    keyword coverage.
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

    return {
        "year": year,
        "month": month,
        "month_name": calendar_data[
            "month_name"
        ],
        "days_in_month": len(days),
        "keyword_days": len(
            keyword_days
        ),
        "empty_days": (
            len(days)
            - len(keyword_days)
        ),
    }


# ============================================================
# Get a single calendar day
# ============================================================

def get_calendar_day(
    year,
    month,
    day,
):
    """
    Return one day from the monthly calendar.
    """

    calendar_data = build_month_calendar(
        year,
        month,
    )

    for item in calendar_data["days"]:

        if item["day"] == day:

            return item

    raise ValueError(
        "Invalid day for this month."
    )
