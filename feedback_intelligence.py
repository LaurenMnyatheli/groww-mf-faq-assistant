"""Updated feedback intelligence UI: reviews, pulse and RAG fee explainer."""
import json
import pandas as pd
import streamlit as st

from modules.review_analyser import analyse_reviews, to_markdown_report
from modules.product_pulse import generate_weekly_pulse
from modules.fee_rag import build_fee_explainer


def render_feedback_intelligence():
    st.markdown("## Customer Feedback Intelligence")
    st.write(
        "Upload public customer reviews to identify themes, generate an internal product pulse "
        "and investigate fee-related questions using official source material."
    )
    uploaded = st.file_uploader(
        "Upload customer reviews CSV", type=["csv"], key="groww_review_csv",
        help="The file must include a review_text column. Dates and source links are recommended."
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

    st.markdown("### Three supporting customer excerpts")
    for item in result["quotes"]:
        st.markdown(f"> {item['quote']}")
        st.caption(
            f"{item['source']} · {item.get('review_date') or 'Date not recorded'} · "
            f"{item['review_id']} · Theme: {item['theme']}"
        )

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
            use_container_width=True, hide_index=True
        )

    st.markdown("### Weekly Product Pulse")
    st.caption("Draft generated from the review analysis. Review before sharing internally.")
    pulse = generate_weekly_pulse(result)
    st.markdown(pulse)
    st.download_button(
        "Download Weekly Product Pulse", data=pulse,
        file_name="groww_weekly_product_pulse.md", mime="text/markdown",
        use_container_width=True
    )

    st.markdown("### RAG Fee Explainer")
    st.caption(
        "This prototype retrieves from a small, curated set of official Groww, SEBI and AMFI "
        "source excerpts. The fee topic is an investigation candidate, not a proven recurring issue."
    )
    selected_issue = st.selectbox(
        "Fee topic to explain",
        ["Expense ratio vs Total Expense Ratio (TER)"],
        key="groww_fee_issue"
    )
    if st.button("Retrieve official sources and generate explanation", type="primary"):
        with st.spinner("Retrieving official source material..."):
            explainer = build_fee_explainer(selected_issue)
        st.session_state["groww_fee_explainer"] = explainer

    explainer = st.session_state.get("groww_fee_explainer")
    if explainer:
        if explainer.get("status") == "draft":
            st.markdown("**Customer explanation — draft**")
            for bullet in explainer["bullets"]:
                st.markdown(f"- {bullet}")
            st.markdown(f"**Last checked:** {explainer['last_checked']}")
            st.markdown("**Official sources**")
            for source in explainer["sources"][:2]:
                st.markdown(f"- [{source['title']}]({source['url']})")
            st.caption("Retrieval method: " + explainer["retrieval_method"])
            st.download_button(
                "Download fee explainer",
                data="\n".join(
                    ["# Customer Fee Explanation", ""] +
                    [f"- {b}" for b in explainer["bullets"]] +
                    ["", f"Last checked: {explainer['last_checked']}", ""] +
                    [f"- [{s['title']}]({s['url']})" for s in explainer["sources"][:2]]
                ),
                file_name="groww_fee_explainer.md",
                mime="text/markdown",
                use_container_width=True
            )
        else:
            st.warning(explainer.get("message", "Insufficient source evidence."))

    st.download_button(
        "Download review intelligence report",
        data=to_markdown_report(result),
        file_name="groww_review_intelligence.md",
        mime="text/markdown",
        use_container_width=True
    )
    st.download_button(
        "Download analysis results (JSON)",
        data=json.dumps(result, ensure_ascii=False, indent=2),
        file_name="groww_review_analysis.json",
        mime="application/json",
        use_container_width=True
    )
