"""Streamlit UI section for the Groww feedback intelligence prototype."""
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.review_analyser import analyse_reviews, to_markdown_report


def render_feedback_intelligence():
    st.markdown("## Customer Feedback Intelligence")
    st.write(
        "Upload a public customer-review CSV to identify themes and fee-related "
        "signals. This first version uses transparent keyword rules."
    )

    uploaded = st.file_uploader(
        "Upload customer reviews CSV",
        type=["csv"],
        key="groww_review_csv",
        help="The file must include a review_text column. Dates and source links are recommended.",
    )

    if uploaded is None:
        st.info("Upload your review CSV to begin. Do not upload private customer data.")
        st.caption("Expected columns: review_id, review_date, rating, review_text, source, source_url.")
        return

    try:
        df = pd.read_csv(uploaded)
        result = analyse_reviews(df)
    except Exception as exc:
        st.error(f"Could not analyse this CSV: {exc}")
        return

    st.success(f"Analysed {result['total_reviews']} non-empty, de-duplicated review records.")
    st.caption(result["method_note"])

    st.markdown("### Review themes")
    if result["themes"]:
        st.dataframe(pd.DataFrame(result["themes"]), use_container_width=True, hide_index=True)
    else:
        st.warning("No reviews matched the current theme dictionary.")

    st.markdown("### Three supporting customer excerpts")
    for item in result["quotes"]:
        st.markdown(f"> {item['quote']}")
        st.caption(f"{item['source']} · {item['review_date']} · {item['review_id']} · Theme: {item['theme']}")

    st.markdown("### Fee-related confusion")
    if result["recurring_fee_issue"]:
        fee = result["recurring_fee_issue"]
        st.warning(f"Candidate recurring issue: {fee['issue']} — {fee['count']} reviews.")
        st.write("Matched review IDs:", ", ".join(fee["review_ids"]))
    else:
        st.info(result["fee_finding_note"])

    st.markdown("### Other fee-related candidates")
    if result["fee_issue_candidates"]:
        st.dataframe(
            pd.DataFrame([
                {"candidate": item["issue"], "review_count": item["count"]}
                for item in result["fee_issue_candidates"]
            ]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.write("No fee-related phrases matched.")

    report = to_markdown_report(result)
    st.download_button(
        "Download review intelligence report",
        data=report,
        file_name="groww_review_intelligence.md",
        mime="text/markdown",
        use_container_width=True,
    )
    st.download_button(
        "Download analysis results (JSON)",
        data=__import__("json").dumps(result, ensure_ascii=False, indent=2),
        file_name="groww_review_analysis.json",
        mime="application/json",
        use_container_width=True,
    )
