from datetime import datetime
import json

from app.database.database import (
    add_analysis,
    get_analyses,
    get_analysis,
    update_analysis,
    delete_analysis,
)

from app.ai.llm_service import analyze_text


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
# Serialize analysis result
# ============================================================

def serialize_analysis_result(result):
    """
    Convert analysis results into a SQLite-safe value.

    SQLite TEXT fields cannot directly store Python
    lists or dictionaries, so structured results are
    serialized as JSON.

    Examples:

        ["AI", "Python"]
        ->
        '["AI", "Python"]'

        {"label": "happy", "confidence": 0.9}
        ->
        '{"label": "happy", "confidence": 0.9}'
    """

    if result is None:
        return None

    if isinstance(
        result,
        (dict, list)
    ):
        return json.dumps(
            result,
            ensure_ascii=False
        )

    return str(result)


# ============================================================
# Deserialize analysis result
# ============================================================

def deserialize_analysis_result(result):
    """
    Convert a JSON string stored in SQLite back into
    a Python list or dictionary when possible.
    """

    if result is None:
        return None

    if not isinstance(
        result,
        str
    ):
        return result

    try:
        return json.loads(result)

    except (
        json.JSONDecodeError,
        TypeError
    ):
        return result


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

    serialized_result = serialize_analysis_result(
        result
    )

    analysis_id = add_analysis(
        memory_id=memory_id,
        analysis_type=analysis_type,
        result=serialized_result,
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
# Unknown result
# ============================================================

def unknown_result(
    memory_id,
    analysis_type,
    reason="Insufficient information.",
):
    """
    Create an explicit unknown analysis result.

    Memento AI should not invent information when
    there is insufficient evidence.
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
    """

    return create_analysis_result(
        memory_id=memory_id,
        analysis_type=analysis_type,
        result=None,
        confidence=None,
        status="pending",
    )


# ============================================================
# Get analyses for a memory
# ============================================================

def get_memory_analyses(memory_id):
    """
    Get all analysis results associated
    with a memory.

    JSON strings stored in SQLite are converted
    back into Python objects.
    """

    analyses = get_analyses(
        memory_id
    )

    results = []

    for analysis in analyses:

        item = dict(analysis)

        item["result"] = deserialize_analysis_result(
            item.get("result")
        )

        results.append(item)

    return results


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

    item = dict(analysis)

    item["result"] = deserialize_analysis_result(
        item.get("result")
    )

    return item


# ============================================================
# Update analysis
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

    serialized_result = serialize_analysis_result(
        result
    )

    return update_analysis(
        analysis_id=analysis_id,
        result=serialized_result,
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
# Store LLM result
# ============================================================

def store_llm_analysis(
    memory_id,
    llm_result,
):
    """
    Store a validated LLM analysis result
    in the analyses table.

    The LLM result is expected to contain:

        summary
        topics
        mood
        tags
    """

    if not isinstance(
        llm_result,
        dict
    ):
        raise ValueError(
            "LLM analysis result must be a dictionary."
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = llm_result.get(
        "summary"
    )

    if summary is None:

        create_analysis_result(
            memory_id=memory_id,
            analysis_type="summary",
            result=None,
            confidence=0.0,
            status="unknown",
            reason=(
                "The model could not generate "
                "a reliable summary."
            ),
        )

    else:

        create_analysis_result(
            memory_id=memory_id,
            analysis_type="summary",
            result=summary,
            status="completed",
        )

    # --------------------------------------------------------
    # Topics
    # --------------------------------------------------------

    topics = llm_result.get(
        "topics",
        []
    )

    if not topics:

        create_analysis_result(
            memory_id=memory_id,
            analysis_type="topics",
            result=None,
            confidence=0.0,
            status="unknown",
            reason=(
                "No reliable topics could "
                "be identified."
            ),
        )

    else:

        create_analysis_result(
            memory_id=memory_id,
            analysis_type="topics",
            result=topics,
            status="completed",
        )

    # --------------------------------------------------------
    # Mood
    # --------------------------------------------------------

    mood = llm_result.get(
        "mood",
        {}
    )

    if not isinstance(
        mood,
        dict
    ):
        mood = {}

    mood_label = mood.get(
        "label"
    )

    mood_confidence = validate_confidence(
        mood.get(
            "confidence",
            0.0
        )
    )

    mood_reason = mood.get(
        "reason",
        "Insufficient information."
    )

    if mood_label is None:

        create_analysis_result(
            memory_id=memory_id,
            analysis_type="mood",
            result=None,
            confidence=0.0,
            status="unknown",
            reason=mood_reason,
        )

    else:

        create_analysis_result(
            memory_id=memory_id,
            analysis_type="mood",
            result=mood,
            confidence=mood_confidence,
            status="completed",
        )

    # --------------------------------------------------------
    # Tags
    # --------------------------------------------------------

    tags = llm_result.get(
        "tags",
        []
    )

    if not tags:

        create_analysis_result(
            memory_id=memory_id,
            analysis_type="tags",
            result=None,
            confidence=0.0,
            status="unknown",
            reason=(
                "No reliable tags could "
                "be identified."
            ),
        )

    else:

        create_analysis_result(
            memory_id=memory_id,
            analysis_type="tags",
            result=tags,
            status="completed",
        )

    return get_memory_analyses(
        memory_id
    )


# ============================================================
# Analyze and store text memory
# ============================================================

def analyze_and_store_text_memory(
    memory_id,
    content,
):
    """
    Analyze a text memory using DeepSeek
    and store the results in SQLite.

    Pipeline:

        Memory
            ↓
        DeepSeek
            ↓
        Structured result
            ↓
        Validation
            ↓
        SQLite
    """

    if not content or not content.strip():

        raise ValueError(
            "Text memory content cannot be empty."
        )

    try:

        llm_result = analyze_text(
            content
        )

        return store_llm_analysis(
            memory_id=memory_id,
            llm_result=llm_result,
        )

    except Exception as error:

        create_analysis_result(
            memory_id=memory_id,
            analysis_type="summary",
            result=None,
            confidence=0.0,
            status="failed",
            reason=str(error),
        )

        raise


# ============================================================
# Text analysis
# ============================================================

def analyze_text_memory(
    memory_id,
    content,
):
    """
    Analyze and store a text memory.
    """

    if not content or not content.strip():

        raise ValueError(
            "Text memory content cannot be empty."
        )

    return analyze_and_store_text_memory(
        memory_id=memory_id,
        content=content,
    )


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
            f"Unsupported media type: {memory_type}"
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