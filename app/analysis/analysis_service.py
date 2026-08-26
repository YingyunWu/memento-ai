from datetime import datetime

from app.database.database import (
    add_analysis,
    get_analyses,
    get_analysis,
    update_analysis,
    delete_analysis,
)


# ============================================================
# Supported analysis types
# ============================================================

ANALYSIS_TYPES = {
    "summary",
    "topics",
    "mood",
    "tags",
}


# ============================================================
# Analysis statuses
# ============================================================

ANALYSIS_STATUSES = {
    "pending",
    "completed",
    "unknown",
    "failed",
}


# ============================================================
# Validate analysis type
# ============================================================

def validate_analysis_type(analysis_type):
    """
    Validate and normalize an analysis type.
    """

    if not analysis_type:
        raise ValueError(
            "Analysis type cannot be empty."
        )

    analysis_type = analysis_type.lower().strip()

    if analysis_type not in ANALYSIS_TYPES:
        raise ValueError(
            f"Unsupported analysis type: {analysis_type}. "
            f"Supported types are: "
            f"{', '.join(sorted(ANALYSIS_TYPES))}"
        )

    return analysis_type


# ============================================================
# Validate confidence
# ============================================================

def validate_confidence(confidence):
    """
    Validate an optional confidence score.

    Confidence must be between 0 and 1.
    """

    if confidence is None:
        return None

    if not isinstance(
        confidence,
        (int, float)
    ):
        raise ValueError(
            "Confidence must be a number."
        )

    if not 0 <= confidence <= 1:
        raise ValueError(
            "Confidence must be between 0 and 1."
        )

    return float(confidence)


# ============================================================
# Create analysis result
# ============================================================

def create_analysis_result(
    memory_id,
    analysis_type,
    result,
    confidence=None,
    status="completed",
    reason=None,
):
    """
    Create and store a standardized analysis result.

    This function currently does not call an AI model.

    It is responsible for:
        1. Validating the analysis result.
        2. Saving it to the database.
        3. Returning a standardized dictionary.
    """

    analysis_type = validate_analysis_type(
        analysis_type
    )

    confidence = validate_confidence(
        confidence
    )

    if status not in ANALYSIS_STATUSES:
        raise ValueError(
            f"Unsupported analysis status: {status}. "
            f"Supported statuses are: "
            f"{', '.join(sorted(ANALYSIS_STATUSES))}"
        )

    if status == "unknown":

        result = None

        if confidence is None:
            confidence = 0.0

    analysis_id = add_analysis(
        memory_id=memory_id,
        analysis_type=analysis_type,
        result=result,
        confidence=confidence,
        status=status,
        reason=reason,
    )

    return {
        "id": analysis_id,
        "memory_id": memory_id,
        "analysis_type": analysis_type,
        "result": result,
        "confidence": confidence,
        "status": status,
        "reason": reason,
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        ),
    }


# ============================================================
# Unknown / insufficient information
# ============================================================

def unknown_result(
    memory_id,
    analysis_type,
    reason="Insufficient information.",
):
    """
    Create an explicit unknown analysis result.

    Memento AI should not invent information when
    the available memory does not provide enough
    evidence for a reliable conclusion.
    """

    return create_analysis_result(
        memory_id=memory_id,
        analysis_type=analysis_type,
        result=None,
        confidence=0.0,
        status="unknown",
        reason=reason,
    )


# ============================================================
# Pending analysis
# ============================================================

def create_pending_analysis(
    memory_id,
    analysis_type,
):
    """
    Create a pending analysis record.

    This will be useful when an AI analysis job
    has been requested but has not completed yet.
    """

    return create_analysis_result(
        memory_id=memory_id,
        analysis_type=analysis_type,
        result=None,
        confidence=None,
        status="pending",
        reason=None,
    )


# ============================================================
# Get analyses for a memory
# ============================================================

def get_memory_analyses(memory_id):
    """
    Get all analysis results associated
    with a memory.
    """

    analyses = get_analyses(
        memory_id
    )

    return [
        dict(analysis)
        for analysis in analyses
    ]


# ============================================================
# Get one analysis
# ============================================================

def get_single_analysis(analysis_id):
    """
    Get one analysis by ID.
    """

    analysis = get_analysis(
        analysis_id
    )

    if analysis is None:
        return None

    return dict(analysis)


# ============================================================
# Update analysis result
# ============================================================

def edit_analysis(
    analysis_id,
    result=None,
    confidence=None,
    status=None,
    reason=None,
):
    """
    Update an existing analysis result.
    """

    if confidence is not None:

        confidence = validate_confidence(
            confidence
        )

    if status is not None:

        if status not in ANALYSIS_STATUSES:
            raise ValueError(
                f"Unsupported analysis status: {status}"
            )

    return update_analysis(
        analysis_id=analysis_id,
        result=result,
        confidence=confidence,
        status=status,
        reason=reason,
    )


# ============================================================
# Remove analysis
# ============================================================

def remove_analysis(analysis_id):
    """
    Delete an analysis result.
    """

    return delete_analysis(
        analysis_id
    )


# ============================================================
# Text analysis placeholder
# ============================================================

def analyze_text_memory(
    memory_id,
    content,
):
    """
    Prepare a text memory for future AI analysis.

    No AI model is called yet.
    """

    if not content or not content.strip():

        raise ValueError(
            "Text memory content cannot be empty."
        )

    existing_analyses = get_memory_analyses(
        memory_id
    )

    return {
        "memory_id": memory_id,
        "memory_type": "text",
        "status": "pending",
        "message": (
            "Text memory is ready for AI analysis."
        ),
        "analyses": existing_analyses,
    }


# ============================================================
# Media analysis placeholder
# ============================================================

def analyze_media_memory(
    memory_id,
    memory_type,
    content,
):
    """
    Prepare a media memory for future AI analysis.

    Supported media types:
        photo
        music
        video

    No assumptions are made about the media content
    until the corresponding AI capability is connected.
    """

    memory_type = memory_type.lower().strip()

    if memory_type not in {
        "photo",
        "music",
        "video",
    }:

        raise ValueError(
            f"Unsupported memory type: {memory_type}"
        )

    if not content or not content.strip():

        raise ValueError(
            "Media content cannot be empty."
        )

    existing_analyses = get_memory_analyses(
        memory_id
    )

    return {
        "memory_id": memory_id,
        "memory_type": memory_type,
        "status": "pending",
        "message": (
            f"{memory_type.capitalize()} memory "
            "is ready for AI analysis."
        ),
        "analyses": existing_analyses,
    }


# ============================================================
# Unified analysis entry point
# ============================================================

def analyze_memory(
    memory_id,
    memory_type,
    content,
):
    """
    Unified entry point for memory analysis.

    The rest of Memento AI should call this function
    instead of interacting directly with individual
    AI models.
    """

    memory_type = memory_type.lower().strip()

    if memory_type == "text":

        return analyze_text_memory(
            memory_id,
            content,
        )

    if memory_type in {
        "photo",
        "music",
        "video",
    }:

        return analyze_media_memory(
            memory_id,
            memory_type,
            content,
        )

    raise ValueError(
        f"Unsupported memory type: {memory_type}"
    )


# ============================================================
# Supported analysis types
# ============================================================

def get_supported_analysis_types():
    """
    Return supported AI analysis types.
    """

    return sorted(
        ANALYSIS_TYPES
    )