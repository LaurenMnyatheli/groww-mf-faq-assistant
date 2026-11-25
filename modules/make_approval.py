"""Human-approved handoff from Streamlit to Make.com."""
from __future__ import annotations

from datetime import date, datetime, timezone
import requests
import streamlit as st


def _normalise_themes(result: dict) -> list[dict]:
    themes = result.get("top_three_themes") or result.get("themes") or []
    return [
        {
            "theme": item.get("theme", "Unlabelled theme"),
            "count": item.get("count", 0),
            "share_pct": item.get("share_pct", 0),
        }
        for item in themes[:3]
    ]


def build_approval_payload(result: dict, weekly_pulse: str, explainer: dict) -> dict:
    """Build the exact structured payload required by the assignment."""
    if not explainer or explainer.get("status") != "draft":
        raise ValueError("Generate a fee explainer before requesting approval.")

    source_links = [
        {"title": source["title"], "url": source["url"]}
        for source in explainer.get("sources", [])[:2]
    ]
    explanation_bullets = explainer.get("bullets", [])[:6]

    # The analysis currently reports no recurring fee issue. Preserve that finding.
    recurring = result.get("recurring_fee_issue")
    if recurring:
        identified_fee_issue = {
            "issue": recurring.get("issue", "Fee-related confusion"),
            "review_count": recurring.get("count", 0),
            "evidence_status": "recurring_signal_detected",
            "review_ids": recurring.get("review_ids", []),
        }
    else:
        candidates = result.get("fee_issue_candidates", [])
        identified_fee_issue = {
            "issue": "Expense ratio / TER transparency (candidate for investigation)",
            "review_count": next(
                (c.get("count", 0) for c in candidates
                 if "expense" in str(c.get("issue", "")).lower()),
                1 if candidates else 0,
            ),
            "evidence_status": "not_established_as_recurring",
            "note": (
                "The uploaded analysis does not establish a recurring fee misunderstanding. "
                "Treat this as an emerging candidate, not a confirmed recurring issue."
            ),
        }

    today = date.today().isoformat()
    email_body = (
        "WEEKLY PRODUCT PULSE\n\n"
        + weekly_pulse
        + "\n\nCUSTOMER FEE EXPLANATION — REUSABLE SUPPORT SNIPPET\n\n"
        + "\n".join(f"• {bullet}" for bullet in explanation_bullets)
        + f"\n\nLast checked: {explainer.get('last_checked', today)}"
        + "\n\nOfficial sources:\n"
        + "\n".join(f"{s['title']}: {s['url']}" for s in source_links)
        + "\n\nInternal draft. Review before use."
    )

    doc_entry = (
        f"\n\n===== Groww Product Pulse | {today} =====\n\n"
        f"TOP THEMES\n{', '.join(t['theme'] + ' (' + str(t['count']) + ')' for t in _normalise_themes(result))}\n\n"
        f"WEEKLY PULSE\n{weekly_pulse}\n\n"
        f"IDENTIFIED FEE ISSUE\n{identified_fee_issue.get('issue')}\n"
        f"Evidence status: {identified_fee_issue.get('evidence_status')}\n\n"
        f"FEE EXPLANATION\n"
        + "\n".join(f"• {b}" for b in explanation_bullets)
        + "\n\nSOURCE LINKS\n"
        + "\n".join(f"{s['title']}: {s['url']}" for s in source_links)
        + f"\n\nLast checked: {explainer.get('last_checked', today)}\n"
    )

    return {
        "date": today,
        "top_themes": _normalise_themes(result),
        "weekly_pulse": weekly_pulse,
        "identified_fee_issue": identified_fee_issue,
        "explanation_bullets": explanation_bullets,
        "source_links": source_links,
        "doc_entry": doc_entry,
        "email_subject": f"Weekly Product Pulse + Customer Clarification — {today}",
        "email_body": email_body,
        "approved": True,
        "approval_timestamp": datetime.now(timezone.utc).isoformat(),
    }


def render_make_approval(result: dict, weekly_pulse: str, explainer: dict) -> None:
    """Render an explicit human approval gate and send only after button click."""
    st.markdown("### Approval & Distribution")
    st.write(
        "Review both outputs. Nothing is sent to Make, Google Docs or Gmail until "
        "you tick the approval box and click the approval button."
    )

    if not explainer or explainer.get("status") != "draft":
        st.info("Generate the RAG Fee Explainer above before preparing distribution.")
        return

    with st.expander("Preview the information that will be shared", expanded=False):
        st.markdown("**Weekly Product Pulse**")
        st.markdown(weekly_pulse)
        st.markdown("**Fee explanation**")
        for bullet in explainer.get("bullets", [])[:6]:
            st.markdown(f"- {bullet}")
        st.markdown(f"**Last checked:** {explainer.get('last_checked', 'Not supplied')}")
        st.markdown("**Sources**")
        for source in explainer.get("sources", [])[:2]:
            st.markdown(f"- [{source['title']}]({source['url']})")

    approved = st.checkbox(
        "I have reviewed and approve appending this update to Google Docs and creating a Gmail draft.",
        key="groww_make_human_approval",
    )

    if st.button(
        "Approve and send to Make",
        type="primary",
        disabled=not approved,
        key="groww_make_approve_send",
    ):
        try:
            webhook_url = st.secrets["MAKE_WEBHOOK_URL"]
            api_key = st.secrets["MAKE_WEBHOOK_API_KEY"]
        except Exception:
            st.error(
                "Make credentials are missing. Add MAKE_WEBHOOK_URL and "
                "MAKE_WEBHOOK_API_KEY to Streamlit Secrets before approving."
            )
            return

        try:
            payload = build_approval_payload(result, weekly_pulse, explainer)
            response = requests.post(
                webhook_url,
                json=payload,
                headers={"x-make-apikey": api_key},
                timeout=30,
            )
            response.raise_for_status()
            st.success(
                "Approved payload delivered to Make. Check the Make scenario history "
                "to confirm Google Docs append and Gmail draft creation."
            )
            st.session_state["groww_make_last_approval"] = payload["approval_timestamp"]
            st.session_state["groww_make_human_approval"] = False
        except requests.RequestException as exc:
            st.error(f"Could not deliver the approved payload to Make: {exc}")
        except Exception as exc:
            st.error(f"Could not prepare the approved payload: {exc}")
