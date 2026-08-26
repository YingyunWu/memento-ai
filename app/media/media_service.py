from pathlib import Path
from urllib.parse import urlparse
import shutil


# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Directory for user media
MEDIA_DIR = BASE_DIR / "data" / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


def is_valid_url(url):
    """
    Check whether a string looks like a valid HTTP/HTTPS URL.
    """
    try:
        parsed = urlparse(url)

        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.netloc)
        )

    except Exception:
        return False


def save_photo(photo_path, journal_date):
    """
    Copy a photo into Memento AI's local media directory.

    Example:
        original:
            /Users/erinwu/Desktop/photo.jpg

        stored:
            data/media/2026-08-25/photo.jpg

    Returns:
        The stored relative path.
    """

    source = Path(photo_path).expanduser()

    if not source.exists():
        raise FileNotFoundError(
            f"Photo not found: {source}"
        )

    if not source.is_file():
        raise ValueError(
            f"Photo path is not a file: {source}"
        )

    # Create a directory for this journal date.
    journal_media_dir = MEDIA_DIR / journal_date
    journal_media_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    destination = journal_media_dir / source.name

    # Avoid accidentally overwriting an existing file.
    if destination.exists():
        stem = source.stem
        suffix = source.suffix

        counter = 1

        while True:
            new_name = f"{stem}_{counter}{suffix}"
            candidate = journal_media_dir / new_name

            if not candidate.exists():
                destination = candidate
                break

            counter += 1

    shutil.copy2(source, destination)

    # Store a project-relative path in the database.
    relative_path = destination.relative_to(BASE_DIR)

    return str(relative_path)


def validate_music_url(url):
    """
    Validate a music URL.

    Currently accepts any HTTP/HTTPS URL.
    Later we can add platform-specific validation
    for Spotify, Apple Music, YouTube Music, etc.
    """

    url = url.strip()

    if not is_valid_url(url):
        raise ValueError(
            "Invalid music URL. "
            "Please provide a valid http:// or https:// URL."
        )

    return url


def validate_video_url(url):
    """
    Validate a video URL.

    Currently accepts any HTTP/HTTPS URL.
    Later we can add platform-specific support
    for YouTube, Bilibili, Vimeo, etc.
    """

    url = url.strip()

    if not is_valid_url(url):
        raise ValueError(
            "Invalid video URL. "
            "Please provide a valid http:// or https:// URL."
        )

    return url


def get_media_directory(journal_date):
    """
    Return the media directory for a specific journal date.
    """

    journal_media_dir = MEDIA_DIR / journal_date

    journal_media_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return journal_media_dir