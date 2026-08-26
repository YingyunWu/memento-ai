from flask import Flask, render_template, request, redirect, url_for

from app.keyword.keyword_service import (
    get_monthly_keywords,
    generate_daily_keyword_candidates,
    set_final_keyword,
)

from app.memory.memory_service import (
    get_journal_memories,
    create_memory,
)


app = Flask(
    __name__,
    template_folder="app/web/templates",
    static_folder="app/web/static",
)


@app.route("/")
def index():

    return render_template(
        "index.html"
    )


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


@app.route(
    "/day/<journal_date>",
    methods=["GET", "POST"],
)
def day_view(
    journal_date,
):

    if request.method == "POST":

        action = request.form.get(
            "action",
            "memory",
        )

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

                try:

                    candidates = (
                        generate_daily_keyword_candidates(
                            journal_date
                        )
                    )

                    if candidates:

                        set_final_keyword(
                            journal_date,
                            candidates[0],
                            source="ai",
                        )

                except Exception as exc:

                    print(
                        f"AI keyword generation failed: {exc}"
                    )

        elif action == "keyword":

            keyword = request.form.get(
                "keyword",
                "",
            ).strip()

            if keyword:

                try:

                    set_final_keyword(
                        journal_date,
                        keyword,
                        source="user",
                    )

                except Exception as exc:

                    print(
                        f"Keyword update failed: {exc}"
                    )

        return redirect(
            url_for(
                "day_view",
                journal_date=journal_date,
            )
        )


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


if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000,
    )