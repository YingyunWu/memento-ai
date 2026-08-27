import json
import os

from openai import OpenAI


# ============================================================
# Load .env manually
# ============================================================

def load_env_file():
    """
    Load environment variables from the project's .env file.

    This implementation does not require python-dotenv.
    """

    # app/ai/llm_service.py
    #        ↓
    # app/ai
    #        ↓
    # app
    #        ↓
    # project root: memento-ai

    project_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
        )
    )

    env_path = os.path.join(
        project_root,
        ".env",
    )

    if not os.path.exists(env_path):
        return

    with open(
        env_path,
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            line = line.strip()

            # Ignore empty lines
            if not line:
                continue

            # Ignore comments
            if line.startswith("#"):
                continue

            # Ignore invalid lines
            if "=" not in line:
                continue

            key, value = line.split(
                "=",
                1,
            )

            key = key.strip()
            value = value.strip()

            # Remove surrounding double quotes
            if (
                len(value) >= 2
                and value.startswith('"')
                and value.endswith('"')
            ):
                value = value[1:-1]

            # Remove surrounding single quotes
            elif (
                len(value) >= 2
                and value.startswith("'")
                and value.endswith("'")
            ):
                value = value[1:-1]

            # Do not overwrite an existing environment variable
            os.environ.setdefault(
                key,
                value,
            )


# Load .env before reading DEEPSEEK_API_KEY
load_env_file()


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
# DeepSeek client
# ============================================================

def get_client():
    """
    Create and return a DeepSeek API client.
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
# General JSON request
# ============================================================

def generate_json(
    messages,
    model=DEFAULT_MODEL,
    temperature=0.7,
):
    """
    Send a chat request to DeepSeek and return
    the parsed JSON response.

    Args:
        messages:
            OpenAI-compatible message list.

        model:
            DeepSeek model name.

        temperature:
            Sampling temperature.

    Returns:
        Python dictionary.
    """

    client = get_client()

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        response_format={
            "type": "json_object"
        },
    )

    raw_content = (
        response.choices[0]
        .message
        .content
    )

    if not raw_content:

        raise ValueError(
            "DeepSeek returned an empty response."
        )

    raw_content = raw_content.strip()

    try:

        result = json.loads(
            raw_content
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            "DeepSeek returned invalid JSON."
        ) from error

    return result


# ============================================================
# Analyze text memory
# ============================================================

def analyze_text(
    content,
    model=DEFAULT_MODEL,
):
    """
    Analyze a text memory using DeepSeek.

    Returns structured JSON containing:

        summary
        topics
        mood
        tags
    """

    if not content or not content.strip():

        raise ValueError(
            "Memory content cannot be empty."
        )

    system_prompt = """
You are the AI analysis engine for Memento AI,
a personal multimodal memory and digital journal system.

Your job is to analyze a user's memory carefully
and return structured information.

Important principles:

1. Do not invent facts.
2. Do not overinterpret short memories.
3. Do not infer information that is not supported
   by the memory.
4. If there is insufficient evidence, use null
   where appropriate.
5. Keep summaries concise and factual.
6. Topics should describe what the memory
   is actually about.
7. Tags should be useful and specific.
8. Mood should only be identified when there is
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

    user_prompt = (
        "Analyze the following memory:\n\n"
        + content.strip()
    )

    result = generate_json(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        model=model,
        temperature=0.2,
    )

    return validate_analysis_result(
        result
    )


# ============================================================
# Validate analysis result
# ============================================================

def validate_analysis_result(
    result,
):
    """
    Validate the structured result returned
    by the LLM.
    """

    if not isinstance(
        result,
        dict,
    ):

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

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = result["summary"]

    if (
        summary is not None
        and not isinstance(
            summary,
            str,
        )
    ):

        raise ValueError(
            "summary must be a string or null."
        )

    # --------------------------------------------------------
    # Topics
    # --------------------------------------------------------

    topics = result["topics"]

    if not isinstance(
        topics,
        list,
    ):

        raise ValueError(
            "topics must be a list."
        )

    if not all(
        isinstance(topic, str)
        for topic in topics
    ):

        raise ValueError(
            "Every topic must be a string."
        )

    # --------------------------------------------------------
    # Tags
    # --------------------------------------------------------

    tags = result["tags"]

    if not isinstance(
        tags,
        list,
    ):

        raise ValueError(
            "tags must be a list."
        )

    if not all(
        isinstance(tag, str)
        for tag in tags
    ):

        raise ValueError(
            "Every tag must be a string."
        )

    # --------------------------------------------------------
    # Mood
    # --------------------------------------------------------

    mood = result["mood"]

    if not isinstance(
        mood,
        dict,
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

    label = mood["label"]

    if (
        label is not None
        and not isinstance(
            label,
            str,
        )
    ):

        raise ValueError(
            "mood.label must be a string or null."
        )

    confidence = mood["confidence"]

    if not isinstance(
        confidence,
        (int, float),
    ):

        raise ValueError(
            "mood.confidence must be a number."
        )

    if not 0 <= confidence <= 1:

        raise ValueError(
            "mood.confidence must be between 0 and 1."
        )

    reason = mood["reason"]

    if not isinstance(
        reason,
        str,
    ):

        raise ValueError(
            "mood.reason must be a string."
        )

    return result
