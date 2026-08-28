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
    get_memory,
    create_memory,
    edit_memory,
    remove_memory,
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
# Helper: normalize photo path
# ============================================================

def normalize_photo_path(photo_path):
    """
    Normalize a photo path stored in the database.

    Preferred database format:

        2026-08-28/abc123.jpg

    Older records may contain:

        data/media/2026-08-28/abc123.jpg

    or:

        /data/media/2026-08-28/abc123.jpg
    """

    if not photo_path:
        return ""

    photo_path = str(photo_path).strip()

    if not photo_path:
        return ""

    photo_path = photo_path.replace(
        "\\",
        "/",
    )

    while photo_path.startswith("/"):
        photo_path = photo_path[1:]

    prefixes = (
        "data/media/",
        "media/",
    )

    for prefix in prefixes:

        if photo_path.startswith(prefix):

            photo_path = photo_path[
                len(prefix):
            ]

            break

    return photo_path


# ============================================================
# Helper: prepare memories for templates
# ============================================================

def prepare_memories(memories):

    prepared = []

    for memory in memories:

        item = dict(memory)

        if item.get("memory_type") == "photo":

            raw_photo_path = (
                item.get("file_path")
                or item.get("content")
                or ""
            )

            item["photo_path"] = (
                normalize_photo_path(
                    raw_photo_path
                )
            )

        else:

            item["photo_path"] = ""

        prepared.append(item)

    return prepared


# ============================================================
# Helper: delete physical photo
# ============================================================

def delete_photo_file(file_path):

    normalized_path = normalize_photo_path(
        file_path
    )

    if not normalized_path:
        return

    physical_path = (
        MEDIA_FOLDER
        / normalized_path
    )

    try:

        physical_path = (
            physical_path.resolve()
        )

        media_root = (
            MEDIA_FOLDER.resolve()
        )

        if media_root not in physical_path.parents:

            raise ValueError(
                "Invalid media file path."
            )

        if physical_path.exists():

            physical_path.unlink()

            print(
                "[MEDIA] Deleted:",
                physical_path,
            )

    except Exception as error:

        print(
            "[MEDIA] Could not delete:",
            error,
        )


# ============================================================
# Media
# ============================================================

@app.route("/media/<path:filename>")
def media(filename):

    filename = normalize_photo_path(
        filename
    )

    print(
        "[MEDIA] Request:",
        filename,
    )

    physical_path = (
        MEDIA_FOLDER
        / filename
    )

    print(
        "[MEDIA] Physical path:",
        physical_path,
    )

    print(
        "[MEDIA] Exists:",
        physical_path.exists(),
    )

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
            "[KEYWORD] Could not load keyword:",
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

    if month < 1:

        year -= 1
        month = 12

    elif month > 12:

        year += 1
        month = 1

    try:

        keywords = get_monthly_keywords(
            year,
            month,
        )

    except Exception as error:

        print(
            "[CALENDAR] Could not load keywords:",
            error,
        )

        keywords = []

    today = date.today().isoformat()

    if month == 1:

        previous_year = year - 1
        previous_month = 12

    else:

        previous_year = year
        previous_month = month - 1

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

        # ----------------------------------------------------
        # DEBUG INFORMATION
        # ----------------------------------------------------

        print("")
        print("=" * 70)
        print("[POST] /day/" + journal_date)
        print("=" * 70)

        print(
            "[POST] form:",
            dict(request.form),
        )

        print(
            "[POST] files:",
            list(request.files.keys()),
        )

        for key in request.files:

            files = request.files.getlist(
                key
            )

            print(
                f"[POST] files[{key!r}] count:",
                len(files),
            )

            for index, file in enumerate(files):

                print(
                    f"[POST] file {index}:",
                    {
                        "filename": file.filename,
                        "content_type": file.content_type,
                        "content_length": file.content_length,
                    }
                )

        action = request.form.get(
            "action",
            "",
        )

        print(
            "[POST] ACTION:",
            repr(action),
        )

        # ====================================================
        # Add memory
        # ====================================================

        if action == "memory":

            content = request.form.get(
                "content",
                "",
            ).strip()

            print(
                "[MEMORY] Content:",
                repr(content),
            )

            if content:

                create_memory(
                    journal_date=journal_date,
                    memory_type="text",
                    content=content,
                    source_type="text",
                )

                print(
                    "[MEMORY] Text memory created."
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

            if memory_id:

                try:

                    memory_id_int = int(
                        memory_id
                    )

                    if content:

                        edit_memory(
                            memory_id=memory_id_int,
                            new_content=content,
                        )

                    else:

                        remove_memory(
                            memory_id=memory_id_int
                        )

                except Exception as error:

                    print(
                        "[MEMORY] Could not edit/delete:",
                        error,
                    )


        # ====================================================
        # Delete memory
        # ====================================================

        elif action == "delete_memory":

            memory_id = request.form.get(
                "memory_id",
                "",
            )

            if memory_id:

                try:

                    memory_id_int = int(
                        memory_id
                    )

                    memory = get_memory(
                        memory_id_int
                    )

                    if memory is None:

                        raise ValueError(
                            f"Memory {memory_id} does not exist."
                        )

                    old_file_path = None

                    if (
                        memory["memory_type"]
                        == "photo"
                    ):

                        old_file_path = (
                            memory["file_path"]
                            or ""
                        )

                    remove_memory(
                        memory_id=memory_id_int
                    )

                    if old_file_path:

                        delete_photo_file(
                            old_file_path
                        )

                except Exception as error:

                    print(
                        "[MEMORY] Could not delete:",
                        error,
                    )


        # ====================================================
        # Replace photo
        # ====================================================

        elif action == "replace_photo":

            memory_id = request.form.get(
                "memory_id",
                "",
            )

            photo = request.files.get(
                "photo"
            )

            print(
                "[REPLACE] memory_id:",
                memory_id,
            )

            print(
                "[REPLACE] photo:",
                photo,
            )

            if photo:

                print(
                    "[REPLACE] filename:",
                    photo.filename,
                )

            if (
                memory_id
                and photo
                and photo.filename
            ):

                try:

                    memory_id_int = int(
                        memory_id
                    )

                    memory = get_memory(
                        memory_id_int
                    )

                    if memory is None:

                        raise ValueError(
                            f"Memory {memory_id} does not exist."
                        )

                    if (
                        memory["memory_type"]
                        != "photo"
                    ):

                        raise ValueError(
                            "Only photo memories can be replaced."
                        )

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

                        raise ValueError(
                            "Unsupported image type: "
                            + extension
                        )

                    journal_media_folder = (
                        MEDIA_FOLDER
                        / journal_date
                    )

                    journal_media_folder.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    unique_filename = (
                        f"{uuid4().hex}"
                        f"{extension}"
                    )

                    new_file_path = (
                        journal_media_folder
                        / unique_filename
                    )

                    photo.save(
                        new_file_path
                    )

                    if not new_file_path.exists():

                        raise IOError(
                            "Photo file was not saved."
                        )

                    relative_path = (
                        new_file_path
                        .relative_to(
                            MEDIA_FOLDER
                        )
                        .as_posix()
                    )

                    old_file_path = (
                        memory["file_path"]
                        or ""
                    )

                    edit_memory(
                        memory_id=memory_id_int,
                        new_file_path=relative_path,
                    )

                    if old_file_path:

                        normalized_old_path = (
                            normalize_photo_path(
                                old_file_path
                            )
                        )

                        if (
                            normalized_old_path
                            != relative_path
                        ):

                            delete_photo_file(
                                old_file_path
                            )

                    print(
                        "[REPLACE] SUCCESS:",
                        relative_path,
                    )

                except Exception as error:

                    print(
                        "[REPLACE] ERROR:",
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
                        "[KEYWORD] Could not save:",
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
                    "[KEYWORD] AI regeneration failed:",
                    error,
                )


        # ====================================================
        # PHOTO UPLOAD
        # ====================================================

        elif action == "photo":

            print("")
            print(
                "[PHOTO] ================================"
            )

            photos = request.files.getlist(
                "photo"
            )

            print(
                "[PHOTO] request.files:",
                request.files,
            )

            print(
                "[PHOTO] photo count:",
                len(photos),
            )

            uploaded_count = 0

            for index, photo in enumerate(photos):

                print(
                    f"[PHOTO] Processing file #{index + 1}"
                )

                print(
                    "[PHOTO] filename:",
                    repr(photo.filename),
                )

                print(
                    "[PHOTO] content_type:",
                    photo.content_type,
                )

                if not photo:

                    print(
                        "[PHOTO] Empty file object."
                    )

                    continue

                if not photo.filename:

                    print(
                        "[PHOTO] Empty filename."
                    )

                    continue

                try:

                    original_filename = (
                        secure_filename(
                            photo.filename
                        )
                    )

                    print(
                        "[PHOTO] secure filename:",
                        original_filename,
                    )

                    extension = Path(
                        original_filename
                    ).suffix.lower()

                    print(
                        "[PHOTO] extension:",
                        extension,
                    )

                    if (
                        extension
                        not in ALLOWED_IMAGE_EXTENSIONS
                    ):

                        print(
                            "[PHOTO] Unsupported image type:",
                            extension,
                        )

                        continue

                    journal_media_folder = (
                        MEDIA_FOLDER
                        / journal_date
                    )

                    journal_media_folder.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    unique_filename = (
                        f"{uuid4().hex}"
                        f"{extension}"
                    )

                    file_path = (
                        journal_media_folder
                        / unique_filename
                    )

                    print(
                        "[PHOTO] Saving to:",
                        file_path,
                    )

                    photo.save(
                        file_path
                    )

                    print(
                        "[PHOTO] Saved physical file."
                    )

                    if not file_path.exists():

                        raise IOError(
                            "Photo file was not saved successfully."
                        )

                    print(
                        "[PHOTO] Physical file exists:",
                        file_path.stat().st_size,
                        "bytes",
                    )

                    relative_path = (
                        file_path
                        .relative_to(
                            MEDIA_FOLDER
                        )
                        .as_posix()
                    )

                    print(
                        "[PHOTO] Database path:",
                        relative_path,
                    )

                    memory_id = create_memory(
                        journal_date=journal_date,
                        memory_type="photo",
                        content="",
                        source_type="upload",
                        file_path=relative_path,
                    )

                    print(
                        "[PHOTO] Database memory created:",
                        memory_id,
                    )

                    uploaded_count += 1

                except Exception as error:

                    print(
                        "[PHOTO] ERROR:",
                        repr(error),
                    )

            print(
                "[PHOTO] Successfully uploaded:",
                uploaded_count,
            )

            print(
                "[PHOTO] ================================"
            )
            print("")


        # ====================================================
        # Unknown action
        # ====================================================

        else:

            print(
                "[POST] WARNING: Unknown or missing action:",
                repr(action),
            )


        # ====================================================
        # Redirect after POST
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
        port=5001,
    )
