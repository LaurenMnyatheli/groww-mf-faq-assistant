"""Deterministic weekly product-pulse generator for review intelligence."""
from datetime import date


ACTION_LIBRARY = {
    "App experience and customer support": [
        "Review the highest-volume app reliability and access complaints with Engineering; quantify incidents and affected journeys.",
        "Audit support contact and escalation journeys, including response-time visibility and unresolved-ticket follow-up.",
        "Add clearer in-app status messaging for delayed or failed transactions and account checks.",
    ],
    "Fees and charges": [
        "Review fee and charge disclosures at the point where customers place, switch or redeem investments.",
        "Compare the wording in the app with the latest official scheme and statutory disclosures; escalate inconsistencies.",
        "Create a support-approved explanation of the specific charge only after the relevant official source has been verified.",
    ],
    "Investment information and performance": [
        "Audit the accuracy and freshness of displayed investment, NAV and portfolio information.",
        "Explain the difference between transaction status, units allotted, invested amount and current market value in relevant journeys.",
        "Add clear timestamps and links to the official source of scheme and transaction information.",
    ],
    "Withdrawals and redemptions": [
        "Map the withdrawal and redemption journey, including expected processing times and status updates.",
        "Review cases where customers report delayed credits or unclear settlement amounts.",
        "Make expected timelines, dependencies and escalation routes easier to find before customers submit a request.",
    ],
}

def generate_weekly_pulse(result: dict, pulse_date: str | None = None) -> str:
    """Create a <=250-word internal note from analyse_reviews() output."""
    pulse_date = pulse_date or date.today().isoformat()
    themes = result.get("top_three_themes") or result.get("themes") or []
    quotes = result.get("quotes") or []
    total = result.get("total_reviews", 0)

    lines = [
        f"# Groww Weekly Product Pulse — {pulse_date}",
        f"**Coverage:** {total} public feedback records analysed.",
        "",
        "## Top themes",
    ]
    if themes:
        for item in themes[:3]:
            lines.append(
                f"- {item['theme']}: {item['count']} reviews ({item['share_pct']}%)."
            )
    else:
        lines.append("- No themes matched the current classifier.")

    lines += ["", "## Customer voice"]
    for item in quotes[:3]:
        quote = item.get("quote", "").strip()
        if len(quote) > 220:
            quote = quote[:217].rsplit(" ", 1)[0] + "..."
        lines.append(
            f"- “{quote}” ({item.get('source', 'Source not recorded')}, "
            f"{item.get('review_date') or 'date not recorded'}; "
            f"{item.get('review_id', 'ID not recorded')})."
        )

    top_theme = themes[0]["theme"] if themes else None
    if top_theme == "App experience and customer support":
        observation = (
            "App experience and support is the largest classified theme. "
            "Feedback points to reliability, access, transaction-status and "
            "support-resolution concerns. These are customer-reported issues, "
            "not independently verified incidents."
        )
    elif top_theme == "Fees and charges":
        observation = (
            "Fees and charges is the largest classified theme. Review the exact "
            "charge and disclosure context before treating the comments as evidence "
            "of an incorrect fee."
        )
    elif top_theme == "Investment information and performance":
        observation = (
            "Investment information and performance is the largest classified "
            "theme. Validate reported display or allocation concerns against "
            "transaction records and official scheme information."
        )
    else:
        observation = (
            "The leading theme is a signal for further investigation. Review "
            "individual cases before concluding that the feedback represents a "
            "confirmed product defect."
        )
    lines += ["", "## Key observation", observation, "", "## Product actions"]

    actions = ACTION_LIBRARY.get(top_theme, [
        "Review the highest-volume customer cases and validate the underlying journey.",
        "Identify the responsible product and operational owners and quantify customer impact.",
        "Improve customer-facing status information and support guidance where evidence supports a change.",
    ])
    for action in actions[:3]:
        lines.append(f"- {action}")

    note = "\n".join(lines)
    # Keep a safety margin under the assignment's 250-word limit.
    words = note.split()
    if len(words) > 245:
        note = " ".join(words[:245])
    return note
