import json

from app.database.database import (
    get_connection,
    current_timestamp,
    get_or_create_journal,
)

from app.memory.memory_service import (
    get_memories,
)

from app.ai.llm_service import (
    get_client,
)


# ============================================================
# Configuration
# ============================================================

MAX_AI_KEYWORD_LENGTH = 7
MAX_AI_CANDIDATES = 3


# ============================================================
# User keyword validation
# ============================================================

def validate_user_keyword(keyword):
    """
    Validate a keyword chosen or written by the user.

    User-created keywords have no length restriction.
    """

    if not isinstance(keyword, str):
        raise ValueError(
            "Keyword must be a string."
        )

    keyword = keyword.strip()

    if not keyword:
        raise ValueError(
            "Keyword cannot be empty."
        )

    return keyword


# ============================================================
# AI keyword validation
# ============================================================

def validate_ai_candidates(candidates):
    """
    Validate and clean AI-generated keyword candidates.

    Rules:
        - Must be a list.
        - Maximum 3 candidates.
        - Empty candidates are rejected.
        - Candidates longer than 7 characters are skipped.
        - Duplicate candidates are removed.
        - At least one valid candidate must remain.
    """

    if not isinstance(candidates, list):
        raise ValueError(
            "AI candidates must be a list."
        )

    if not candidates:
        raise ValueError(
            "AI candidates cannot be empty."
        )

    cleaned = []

    for candidate in candidates:

        if not isinstance(candidate, str):
            continue

        candidate = candidate.strip()

        if not candidate:
            continue

        # ----------------------------------------------------
        # Skip candidates that exceed the length limit.
        # Do not fail the entire AI generation.
        # ----------------------------------------------------

        if len(candidate) > MAX_AI_KEYWORD_LENGTH:
            continue

        # ----------------------------------------------------
        # Remove duplicates
        # ----------------------------------------------------

        if candidate not in cleaned:
            cleaned.append(candidate)

        # ----------------------------------------------------
        # Maximum three valid candidates
        # ----------------------------------------------------

        if len(cleaned) >= MAX_AI_CANDIDATES:
            break

    # --------------------------------------------------------
    # At least one valid candidate is required
    # --------------------------------------------------------

    if not cleaned:
        raise ValueError(
            "AI could not generate a valid keyword."
        )

    return cleaned


# ============================================================
# Save AI candidates
# ============================================================

def save_ai_candidates(
    journal_date,
    candidates,
):
    """
    Save AI-generated keyword candidates
    for a journal day.

    Existing final_keyword is preserved.
    """

    candidates = validate_ai_candidates(
        candidates
    )

    journal = get_or_create_journal(
        journal_date
    )

    connection = get_connection()
    cursor = connection.cursor()

    timestamp = current_timestamp()

    candidates_json = json.dumps(
        candidates,
        ensure_ascii=False,
    )

    cursor.execute(
        """
        SELECT id
        FROM daily_keywords
        WHERE journal_id = ?
        """,
        (journal["id"],),
    )

    existing = cursor.fetchone()

    if existing:

        cursor.execute(
            """
            UPDATE daily_keywords
            SET
                ai_candidates = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                candidates_json,
                timestamp,
                existing["id"],
            ),
        )

        keyword_id = existing["id"]

    else:

        cursor.execute(
            """
            INSERT INTO daily_keywords (
                journal_id,
                journal_date,
                ai_candidates,
                user_keyword,
                final_keyword,
                keyword_source,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                journal["id"],
                journal_date,
                candidates_json,
                None,
                None,
                None,
                timestamp,
                timestamp,
            ),
        )

        keyword_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return keyword_id


# ============================================================
# Set final keyword
# ============================================================

def set_final_keyword(
    journal_date,
    keyword,
    source="user",
):
    """
    Set the final keyword for a journal day.

    source:
        ai
        user

    User keywords have no length restriction.
    AI keywords must obey the 7-character limit.
    """

    source = source.lower().strip()

    if source not in {
        "ai",
        "user",
    }:
        raise ValueError(
            "Source must be 'ai' or 'user'."
        )

    if source == "user":

        keyword = validate_user_keyword(
            keyword
        )

    else:

        candidates = validate_ai_candidates(
            [keyword]
        )

        keyword = candidates[0]

    journal = get_or_create_journal(
        journal_date
    )

    connection = get_connection()
    cursor = connection.cursor()

    timestamp = current_timestamp()

    cursor.execute(
        """
        SELECT id
        FROM daily_keywords
        WHERE journal_id = ?
        """,
        (journal["id"],),
    )

    existing = cursor.fetchone()

    if source == "user":
        user_keyword = keyword
    else:
        user_keyword = None

    if existing:

        cursor.execute(
            """
            UPDATE daily_keywords
            SET
                user_keyword = ?,
                final_keyword = ?,
                keyword_source = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                user_keyword,
                keyword,
                source,
                timestamp,
                existing["id"],
            ),
        )

        keyword_id = existing["id"]

    else:

        cursor.execute(
            """
            INSERT INTO daily_keywords (
                journal_id,
                journal_date,
                ai_candidates,
                user_keyword,
                final_keyword,
                keyword_source,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                journal["id"],
                journal_date,
                None,
                user_keyword,
                keyword,
                source,
                timestamp,
                timestamp,
            ),
        )

        keyword_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return keyword_id


# ============================================================
# Generate AI daily keyword candidates
# ============================================================

def generate_daily_keyword_candidates(
    journal_date,
):
    """
    Generate short daily keyword candidates
    from all memories belonging to a journal day.

    DeepSeek provides up to three candidates.

    The first valid candidate is automatically
    selected as the final AI keyword.
    """

    memories = get_memories(
        journal_date
    )

    if not memories:

        raise ValueError(
            f"No memories found for "
            f"{journal_date}."
        )

    memory_lines = []

    for memory in memories:

        # sqlite3.Row does NOT support .get()
        # so we use [] access here.

        memory_type = memory["memory_type"]
        content = memory["content"]

        if not content:
            continue

        memory_lines.append(
            f"[{memory_type}] {content}"
        )

    if not memory_lines:

        raise ValueError(
            f"No usable memory content found "
            f"for {journal_date}."
        )

    daily_content = "\n".join(
        memory_lines
    )

    prompt = f"""
你正在为一款名为 Memento AI 的私人电子日记应用，
为用户的一天提炼非常简短、有记忆点的关键词。

日期：
{journal_date}

当天真实记录：
{daily_content}

请从当天真实记录中提炼最多 3 个关键词候选。

严格遵守以下要求：

1. 每个关键词必须是 1-7 个字符。
2. 尽量控制在 2-7 个字符。
3. 不要凭空创造当天没有发生的事情。
4. 不要强行推断用户没有表达出来的情绪。
5. 不要使用鸡汤式表达。
6. 不要使用“美好的一天”“充实的一天”
   这类空泛总结。
7. 不要写成新闻标题或工作报告。
8. 可以有轻微的文学感、生活感和画面感。
9. 关键词应该像用户多年后翻看月历时，
   能够立刻想起这一天的一个小注脚。
10. 优先保留当天最有辨识度的事件、人物、
    地点、行动或瞬间。
11. 如果当天内容不足以形成可靠关键词，
    返回空列表。
12. 每一个关键词都必须严格不超过 7 个字符。

输出必须是严格 JSON，不要添加任何解释：

{{
    "candidates": [
        "关键词1",
        "关键词2",
        "关键词3"
    ]
}}
"""

    client = get_client()

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": (
                    "你是 Memento AI 的 Daily Keyword "
                    "生成器。你负责从真实日记中提炼简短、"
                    "自然、有记忆点的关键词。"
                    "不要虚构信息。"
                    "不要过度文学化。"
                    "每个关键词必须不超过7个字符。"
                    "严格按照用户要求输出 JSON。"
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.7,
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

    try:

        result = json.loads(
            raw_content
        )

    except json.JSONDecodeError as exc:

        raise ValueError(
            "DeepSeek returned invalid JSON."
        ) from exc

    candidates = result.get(
        "candidates"
    )

    candidates = validate_ai_candidates(
        candidates
    )

    # Save all AI candidates.
    save_ai_candidates(
        journal_date,
        candidates,
    )

    # Automatically use the first AI candidate
    # as the final keyword shown on the calendar.
    set_final_keyword(
        journal_date,
        candidates[0],
        source="ai",
    )

    return candidates


# ============================================================
# Get one day's keyword
# ============================================================

def get_daily_keyword(
    journal_date,
):
    """
    Get keyword information for one journal day.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            journal_id,
            journal_date,
            ai_candidates,
            user_keyword,
            final_keyword,
            keyword_source,
            created_at,
            updated_at
        FROM daily_keywords
        WHERE journal_date = ?
        """,
        (journal_date,),
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    result = dict(row)

    if result["ai_candidates"]:

        result["ai_candidates"] = json.loads(
            result["ai_candidates"]
        )

    else:

        result["ai_candidates"] = []

    return result


# ============================================================
# Get monthly keywords
# ============================================================

def get_monthly_keywords(
    year,
    month,
):
    """
    Get final keywords for a month.

    This is the data source
    for the monthly calendar UI.
    """

    if not 1 <= month <= 12:

        raise ValueError(
            "Month must be between 1 and 12."
        )

    month_prefix = (
        f"{year:04d}-{month:02d}-"
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            journal_date,
            final_keyword,
            keyword_source
        FROM daily_keywords
        WHERE journal_date LIKE ?
          AND final_keyword IS NOT NULL
          AND final_keyword != ''
        ORDER BY journal_date ASC
        """,
        (
            month_prefix + "%",
        ),
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]

# ============================================================
# Force regenerate daily AI keyword
# ============================================================

def regenerate_daily_keyword(
    journal_date,
):
    """
    Force regeneration of the daily AI keyword.

    This function is used when the user explicitly
    asks Memento AI to regenerate the keyword.

    Unlike the automatic refresh logic:

        - It ignores the current keyword_source.
        - It always asks AI to regenerate the keyword.
        - The resulting keyword becomes AI-owned.

    Returns:
        A list of validated AI keyword candidates.
    """

    candidates = generate_daily_keyword_candidates(
        journal_date
    )

    return candidates