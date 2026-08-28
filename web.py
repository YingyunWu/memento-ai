from pathlib import Path
from uuid import uuid4
from datetime import date

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
)

from werkzeug.utils import secure_filename


from app.keyword.keyword_service import (
    get_monthly_keywords,
    set_final_keyword,
    regenerate_daily_keyword,
)

from app.memory.memory_service import (
    get_journal_memories,
    create_memory,
    edit_memory,
)


# ============================================================
# Flask
# ============================================================

app = Flask(
    __name__,
    template_folder="app/web/templates",
    static_folder="app/web/static",
)


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

MEDIA_FOLDER = (
    PROJECT_ROOT
    / "data"
    / "media"
)

MEDIA_FOLDER.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# Supported image formats
# ============================================================

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".heic",
    ".heif",
}


# ============================================================
# Helper
# ============================================================

def prepare_memories(memories):
    """
    Normalize memory records before passing them
    to the templates.

    Photo memories may store their path in:

        file_path

    or:

        content

    Both are normalized into:

        photo_path
    """

    prepared = []

    for memory in memories:

        item = dict(memory)

        if item.get("memory_type") == "photo":

            photo_path = (
                item.get("file_path")
                or item.get("content")
                or ""
            )

            photo_path = str(photo_path).strip()

            # Normalize Windows-style separators.
            photo_path = photo_path.replace(
                "\\",
                "/",
            )

            # Remove common project prefixes.
            if photo_path.startswith(
                "data/media/"
            ):

                photo_path = photo_path[
                    len("data/media/") :
                ]

            elif photo_path.startswith(
                "/data/media/"
            ):

                photo_path = photo_path[
                    len("/data/media/") :
                ]

            elif photo_path.startswith(
                "media/"
            ):

                photo_path = photo_path[
                    len("media/") :
                ]

            elif photo_path.startswith(
                "/media/"
            ):

                photo_path = photo_path[
                    len("/media/") :
                ]

            item["photo_path"] = photo_path

        else:

            item["photo_path"] = ""

        prepared.append(item)

    return prepared


# ============================================================
# Media
# ============================================================

@app.route("/media/<path:filename>")
def media(filename):
    """
    Serve files stored inside:

        data/media/

    Database example:

        data/media/2026-08-28/abc123.jpg

    Browser URL:

        /media/2026-08-28/abc123.jpg
    """

    return send_from_directory(
        MEDIA_FOLDER,
        filename,
    )


# ============================================================
# Find today's keyword
# ============================================================

def get_keyword_for_date(journal_date):

    try:

        year = int(
            journal_date[:4]
        )

        month = int(
            journal_date[5:7]
        )

        monthly_keywords = (
            get_monthly_keywords(
                year,
                month,
            )
        )

    except Exception as error:

        print(
            "Could not load keyword:",
            error,
        )

        return None

    for item in monthly_keywords:

        item = dict(item)

        if (
            item.get("journal_date")
            == journal_date
        ):

            return item

    return None


# ============================================================
# Home
# ============================================================

@app.route("/")
def index():

    today = date.today().isoformat()

    memories = get_journal_memories(
        today
    )

    memories = prepare_memories(
        memories
    )

    keyword = get_keyword_for_date(
        today
    )

    return render_template(
        "index.html",

        today=today,

        memories=memories,

        keyword=keyword,
    )


# ============================================================
# Calendar
# ============================================================

@app.route(
    "/calendar/<int:year>/<int:month>"
)
def calendar_view(year, month):

    # --------------------------------------------------------
    # Normalize month.
    # --------------------------------------------------------

    if month < 1:

        year -= 1
        month = 12

    elif month > 12:

        year += 1
        month = 1

    # --------------------------------------------------------
    # Keywords.
    # --------------------------------------------------------

    try:

        keywords = get_monthly_keywords(
            year,
            month,
        )

    except Exception as error:

        print(
            "Could not load monthly keywords:",
            error,
        )

        keywords = []

    # --------------------------------------------------------
    # Today.
    # --------------------------------------------------------

    today = date.today().isoformat()

    # --------------------------------------------------------
    # Previous month.
    # --------------------------------------------------------

    if month == 1:

        previous_year = year - 1
        previous_month = 12

    else:

        previous_year = year
        previous_month = month - 1

    # --------------------------------------------------------
    # Next month.
    # --------------------------------------------------------

    if month == 12:

        next_year = year + 1
        next_month = 1

    else:

        next_year = year
        next_month = month + 1

    return render_template(
        "calendar.html",

        year=year,
        month=month,

        keywords=keywords,

        today=today,

        previous_year=previous_year,
        previous_month=previous_month,

        next_year=next_year,
        next_month=next_month,
    )


# ============================================================
# Day
# ============================================================

@app.route(
    "/day/<journal_date>",
    methods=["GET", "POST"],
)
def day_view(journal_date):

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        action = request.form.get(
            "action",
            "",
        )


        # ====================================================
        # Add memory
        # ====================================================

        if action == "memory":

            content = request.form.get(
                "content",
                "",
            ).strip()

            if content:

                create_memory(
                    journal_date=journal_date,
                    memory_type="text",
                    content=content,
                    source_type="text",
                )


        # ====================================================
        # Edit memory
        # ====================================================

        elif action == "edit_memory":

            memory_id = request.form.get(
                "memory_id",
                "",
            )

            content = request.form.get(
                "content",
                "",
            ).strip()

            if memory_id and content:

                try:

                    edit_memory(
                        memory_id=int(
                            memory_id
                        ),
                        content=content,
                    )

                except Exception as error:

                    print(
                        "Could not edit memory:",
                        error,
                    )


        # ====================================================
        # User keyword
        # ====================================================

        elif action == "keyword":

            keyword = request.form.get(
                "keyword",
                "",
            ).strip()

            if keyword:

                try:

                    set_final_keyword(
                        journal_date=journal_date,
                        keyword=keyword,
                        source="user",
                    )

                except Exception as error:

                    print(
                        "Could not save keyword:",
                        error,
                    )


        # ====================================================
        # AI keyword
        # ====================================================

        elif action == "ai_keyword":

            try:

                regenerate_daily_keyword(
                    journal_date
                )

            except Exception as error:

                print(
                    "AI keyword regeneration failed:",
                    error,
                )


        # ====================================================
        # Photo upload
        # ====================================================

        elif action == "photo":

            photos = request.files.getlist(
                "photo"
            )

            for photo in photos:

                if not photo:
                    continue

                if not photo.filename:
                    continue

                original_filename = (
                    secure_filename(
                        photo.filename
                    )
                )

                extension = Path(
                    original_filename
                ).suffix.lower()

                if (
                    extension
                    not in ALLOWED_IMAGE_EXTENSIONS
                ):

                    print(
                        "Unsupported image type:",
                        extension,
                    )

                    continue

                # ------------------------------------------------
                # Date-specific folder.
                # ------------------------------------------------

                journal_media_folder = (
                    MEDIA_FOLDER
                    / journal_date
                )

                journal_media_folder.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                # ------------------------------------------------
                # Unique filename.
                # ------------------------------------------------

                unique_filename = (
                    f"{uuid4().hex}"
                    f"{extension}"
                )

                file_path = (
                    journal_media_folder
                    / unique_filename
                )

                # ------------------------------------------------
                # Save.
                # ------------------------------------------------

                photo.save(
                    file_path
                )

                # ------------------------------------------------
                # Store path relative to data/media.
                #
                # This is important.
                #
                # Database:
                #
                # 2026-08-28/abc123.jpg
                #
                # Browser:
                #
                # /media/2026-08-28/abc123.jpg
                # ------------------------------------------------

                relative_path = (
                    file_path
                    .relative_to(
                        MEDIA_FOLDER
                    )
                    .as_posix()
                )

                create_memory(
                    journal_date=journal_date,
                    memory_type="photo",
                    content="",
                    source_type="upload",
                    file_path=relative_path,
                )


        # ====================================================
        # Redirect after POST.
        # ====================================================

        return redirect(
            url_for(
                "day_view",
                journal_date=journal_date,
            )
        )


    # ========================================================
    # GET
    # ========================================================

    memories = get_journal_memories(
        journal_date
    )

    memories = prepare_memories(
        memories
    )

    keyword = get_keyword_for_date(
        journal_date
    )

    return render_template(
        "day.html",

        journal_date=journal_date,

        memories=memories,

        keyword=keyword,
    )


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000,
    )