from pathlib import Path
from uuid import uuid4

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
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
# Upload configuration
# ============================================================

UPLOAD_FOLDER = (
    Path(app.static_folder)
    / "uploads"
)

UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True,
)


ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
}


# ============================================================
# Home
# ============================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# ============================================================
# Calendar
# ============================================================

@app.route(
    "/calendar/<int:year>/<int:month>"
)
def calendar_view(
    year,
    month,
):

    keywords = get_monthly_keywords(
        year,
        month,
    )

    return render_template(
        "calendar.html",
        year=year,
        month=month,
        keywords=keywords,
    )


# ============================================================
# Day
# ============================================================

@app.route(
    "/day/<journal_date>",
    methods=["GET", "POST"],
)
def day_view(
    journal_date,
):

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        action = request.form.get(
            "action",
            "",
        )


        # ====================================================
        # Add text memory
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
        # Upload photo
        # ====================================================

        elif action == "photo":

            photo = request.files.get(
                "photo"
            )

            if photo and photo.filename:

                original_filename = secure_filename(
                    photo.filename
                )

                extension = Path(
                    original_filename
                ).suffix.lower()


                # --------------------------------------------
                # Validate extension
                # --------------------------------------------

                if extension not in ALLOWED_IMAGE_EXTENSIONS:

                    print(
                        "Unsupported image type: "
                        f"{extension}"
                    )

                    return redirect(
                        url_for(
                            "day_view",
                            journal_date=journal_date,
                        )
                    )


                # --------------------------------------------
                # Generate unique filename
                # --------------------------------------------

                unique_filename = (
                    f"{uuid4().hex}"
                    f"{extension}"
                )


                # --------------------------------------------
                # Save file
                # --------------------------------------------

                file_path = (
                    UPLOAD_FOLDER
                    / unique_filename
                )

                photo.save(
                    file_path
                )


                # --------------------------------------------
                # Database path
                # --------------------------------------------

                relative_path = (
                    f"static/uploads/"
                    f"{unique_filename}"
                )


                # --------------------------------------------
                # Create photo memory
                # --------------------------------------------

                try:

                    create_memory(
                        journal_date=journal_date,
                        memory_type="photo",
                        content="",
                        source_type="upload",
                        file_path=relative_path,
                    )

                except Exception as error:

                    print(
                        "Photo memory creation failed: "
                        f"{error}"
                    )

                    # Remove uploaded file if database
                    # insertion fails.

                    if file_path.exists():

                        file_path.unlink()


        # ====================================================
        # Edit existing memory
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

                edit_memory(
                    memory_id=int(memory_id),
                    new_content=content,
                )


        # ====================================================
        # User edits keyword
        # ====================================================

        elif action == "keyword":

            keyword = request.form.get(
                "keyword",
                "",
            ).strip()

            if keyword:

                set_final_keyword(
                    journal_date=journal_date,
                    keyword=keyword,
                    source="user",
                )


        # ====================================================
        # Explicit AI keyword regeneration
        # ====================================================

        elif action == "ai_keyword":

            try:

                regenerate_daily_keyword(
                    journal_date
                )

            except Exception as error:

                print(
                    "Manual AI keyword update failed: "
                    f"{error}"
                )


        # ====================================================
        # Redirect after POST
        # ========================================================

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


    keyword_data = None


    monthly_keywords = get_monthly_keywords(
        int(journal_date[:4]),
        int(journal_date[5:7]),
    )


    for item in monthly_keywords:

        if item["journal_date"] == journal_date:

            keyword_data = item

            break


    return render_template(
        "day.html",
        journal_date=journal_date,
        memories=memories,
        keyword=keyword_data,
    )


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )