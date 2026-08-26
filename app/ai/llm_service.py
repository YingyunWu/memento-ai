import json
import os

from openai import OpenAI


# ============================================================
# Configuration
# ============================================================

DEEPSEEK_API_KEY = os.getenv(
    "DEEPSEEK_API_KEY"
)

DEEPSEEK_BASE_URL = (
    "https://api.deepseek.com"
)

DEFAULT_MODEL = "deepseek-chat"


# ============================================================
# Client
# ============================================================

def get_client():
    """
    Create a DeepSeek client.

    The API key is loaded from the environment.
    """

    if not DEEPSEEK_API_KEY:

        raise RuntimeError(
            "DEEPSEEK_API_KEY environment variable "
            "is not configured."
        )

    return OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
    )


# ============================================================
# System prompt
# ============================================================

SYSTEM_PROMPT = """
You are the AI analysis engine for Memento AI,
a personal multimodal memory and digital journal system.

Your job is to analyze a user's memory carefully
and return structured information.

Important principles:

1. Do not invent facts.
2. Do not infer sensitive personal information.
3. Do not overinterpret short memories.
4. If there is insufficient evidence, use null
   and explain why.
5. Keep summaries concise and factual.
6. Topics should describe what the memory is actually about.
7. Tags should be useful and specific.
8. Mood must only be identified when there is
   sufficient textual evidence.

Return ONLY valid JSON.

The JSON must contain exactly these fields:

{
    "summary": string or null,
    "topics": array of strings,
    "mood": {
        "label": string or null,
        "confidence": number,
        "reason": string
    },
    "tags": array of strings
}

Confidence must be between 0 and 1.
"""


# ============================================================
# Analyze text memory
# ============================================================

def analyze_text(
    content,
    model=DEFAULT_MODEL,
):
    """
    Analyze a text memory using DeepSeek.

    Returns:
        A Python dictionary containing
        structured analysis results.
    """

    if not content or not content.strip():

        raise ValueError(
            "Memory content cannot be empty."
        )

    client = get_client()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "Analyze the following memory:\n\n"
                    + content.strip()
                ),
            },
        ],
        temperature=0.2,
    )

    raw_content = (
        response.choices[0]
        .message
        .content
        .strip()
    )

    try:

        result = json.loads(
            raw_content
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            "DeepSeek returned invalid JSON."
        ) from error

    return validate_analysis_result(
        result
    )


# ============================================================
# Validate result
# ============================================================

def validate_analysis_result(result):
    """
    Validate the structure returned by the LLM.
    """

    if not isinstance(result, dict):

        raise ValueError(
            "Analysis result must be a dictionary."
        )

    required_fields = {
        "summary",
        "topics",
        "mood",
        "tags",
    }

    missing_fields = (
        required_fields
        - result.keys()
    )

    if missing_fields:

        raise ValueError(
            "Analysis result is missing fields: "
            + ", ".join(
                sorted(missing_fields)
            )
        )

    if not isinstance(
        result["topics"],
        list
    ):

        raise ValueError(
            "topics must be a list."
        )

    if not isinstance(
        result["tags"],
        list
    ):

        raise ValueError(
            "tags must be a list."
        )

    mood = result["mood"]

    if not isinstance(
        mood,
        dict
    ):

        raise ValueError(
            "mood must be an object."
        )

    if "label" not in mood:
        raise ValueError(
            "mood.label is required."
        )

    if "confidence" not in mood:
        raise ValueError(
            "mood.confidence is required."
        )

    if "reason" not in mood:
        raise ValueError(
            "mood.reason is required."
        )

    confidence = mood["confidence"]

    if not isinstance(
        confidence,
        (int, float)
    ):

        raise ValueError(
            "mood.confidence must be a number."
        )

    if not 0 <= confidence <= 1:

        raise ValueError(
            "mood.confidence must be between 0 and 1."
        )

    return result