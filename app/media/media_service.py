from pathlib import Path
from urllib.parse import urlparse
import shutil
import subprocess


# ============================================================
# Project paths
# ============================================================

# Project root:
# memento-ai/
BASE_DIR = Path(__file__).resolve().parents[2]

# Media storage directory:
# memento-ai/data/media/
MEDIA_DIR = BASE_DIR / "data" / "media"

MEDIA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Supported image formats
# ============================================================

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".heic",
    ".heif",
}


# ============================================================
# Supported video formats
# ============================================================

VIDEO_EXTENSIONS = {
    ".mov",
    ".mp4",
}


# ============================================================
# URL validation
# ============================================================

def is_valid_url(url):
    """
    Check whether a URL uses HTTP or HTTPS.
    """

    try:

        parsed = urlparse(url)

        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.netloc)
        )

    except Exception:

        return False


# ============================================================
# Detect photo type
# ============================================================

def detect_photo_type(file_paths):
    """
    Detect whether the selected files represent:

        regular_photo
        live_photo

    Regular photo:
        one image file

    Live Photo:
        one image file + one MOV file

    This function is platform-independent.
    """

    if not file_paths:

        raise ValueError(
            "No files were selected."
        )

    paths = [
        Path(path).expanduser()
        for path in file_paths
    ]

    image_files = [
        path
        for path in paths
        if path.suffix.lower() in IMAGE_EXTENSIONS
    ]

    video_files = [
        path
        for path in paths
        if path.suffix.lower() in VIDEO_EXTENSIONS
    ]

    # --------------------------------------------------------
    # Regular photo
    # --------------------------------------------------------

    if (
        len(paths) == 1
        and len(image_files) == 1
    ):

        return "regular_photo"

    # --------------------------------------------------------
    # Live Photo
    # --------------------------------------------------------

    if (
        len(image_files) == 1
        and len(video_files) == 1
    ):

        return "live_photo"

    raise ValueError(
        "Unsupported photo selection. "
        "Please select one photo or "
        "one photo together with its MOV file "
        "for a Live Photo."
    )


# ============================================================
# Save Photo / Live Photo
# ============================================================

def save_photo(
    file_paths,
    journal_date,
):
    """
    Save a regular photo or Live Photo.

    Regular photo:

        photo.jpg

    Live Photo:

        photo.HEIC
        photo.MOV

    Both are stored inside the same journal directory.

    Returns:

        {
            "type": "regular_photo",
            "photo_path": "...",
            "motion_path": None
        }

    or:

        {
            "type": "live_photo",
            "photo_path": "...",
            "motion_path": "..."
        }
    """

    if isinstance(file_paths, str):

        file_paths = [
            file_paths
        ]

    if not file_paths:

        raise ValueError(
            "No photo files were selected."
        )

    photo_type = detect_photo_type(
        file_paths
    )

    source_paths = [
        Path(path).expanduser()
        for path in file_paths
    ]

    # --------------------------------------------------------
    # Validate source files
    # --------------------------------------------------------

    for source in source_paths:

        if not source.exists():

            raise FileNotFoundError(
                f"File not found: {source}"
            )

        if not source.is_file():

            raise ValueError(
                f"Selected path is not a file: {source}"
            )

    # --------------------------------------------------------
    # Create date-based media directory
    # --------------------------------------------------------

    journal_media_dir = (
        MEDIA_DIR / journal_date
    )

    journal_media_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Save files
    # --------------------------------------------------------

    saved_paths = []

    for source in source_paths:

        destination = (
            journal_media_dir / source.name
        )

        # ----------------------------------------------------
        # Prevent filename conflicts
        # ----------------------------------------------------

        if destination.exists():

            stem = source.stem
            suffix = source.suffix

            counter = 1

            while True:

                new_name = (
                    f"{stem}_{counter}{suffix}"
                )

                candidate = (
                    journal_media_dir / new_name
                )

                if not candidate.exists():

                    destination = candidate

                    break

                counter += 1

        # ----------------------------------------------------
        # Copy original file
        # ----------------------------------------------------

        shutil.copy2(
            source,
            destination
        )

        relative_path = (
            destination.relative_to(BASE_DIR)
        )

        saved_paths.append(
            str(relative_path)
        )

    # --------------------------------------------------------
    # Regular photo
    # --------------------------------------------------------

    if photo_type == "regular_photo":

        return {
            "type": "regular_photo",
            "photo_path": saved_paths[0],
            "motion_path": None,
        }

    # --------------------------------------------------------
    # Live Photo
    # --------------------------------------------------------

    image_path = None
    motion_path = None

    for path in saved_paths:

        suffix = Path(
            path
        ).suffix.lower()

        if suffix in IMAGE_EXTENSIONS:

            image_path = path

        elif suffix in VIDEO_EXTENSIONS:

            motion_path = path

    return {
        "type": "live_photo",
        "photo_path": image_path,
        "motion_path": motion_path,
    }


# ============================================================
# Music URL validation
# ============================================================

def validate_music_url(url):
    """
    Validate a music URL.

    Currently accepts any HTTP/HTTPS URL.
    """

    url = url.strip()

    if not is_valid_url(url):

        raise ValueError(
            "Invalid music URL. "
            "Please provide a valid "
            "http:// or https:// URL."
        )

    return url


# ============================================================
# Video URL validation
# ============================================================

def validate_video_url(url):
    """
    Validate a video URL.

    Currently accepts any HTTP/HTTPS URL.
    """

    url = url.strip()

    if not is_valid_url(url):

        raise ValueError(
            "Invalid video URL. "
            "Please provide a valid "
            "http:// or https:// URL."
        )

    return url


# ============================================================
# Media directory
# ============================================================

def get_media_directory(journal_date):
    """
    Get the media directory associated with
    a specific journal date.
    """

    journal_media_dir = (
        MEDIA_DIR / journal_date
    )

    journal_media_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return journal_media_dir