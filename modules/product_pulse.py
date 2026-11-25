"""Weekly Product Pulse generator with complete, <=250-word output."""
from datetime import date
import re

ACTION_LIBRARY = {
    "App experience and customer support": [
        "Engineering: investigate reported reliability, access and transaction-status issues; validate against incident data.",
        "Support: audit escalation paths, response times and repeat-contact drivers.",
        "Product: clarify transaction and account-status messages in the app.",
    ],
    "Fees and charges": [
        "Review fee disclosures at the point customers invest, switch or redeem.",
        "Validate customer-reported charges against current official scheme documents.",
        "Prepare support guidance only after the specific fee and source are verified.",
    ],
    "Investment information and performance": [
        "Audit the accuracy and freshness of displayed NAV and portfolio information.",
        "Explain invested amount, current value, units allotted and transaction status distinctly.",
        "Validate reported discrepancies against transaction records before classifying defects.",
    ],
    "Withdrawals and redemptions": [
        "Map redemption and withdrawal steps, including expected processing times.",
        "Investigate reported delays and unclear settlement amounts.",
        "Make status updates and escalation routes easier to find.",
    ],
}

def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w₹%'.-]+\b", text))

def _short_quote(value: str, max_words: int = 18) -> str:
    words = value.strip().split()
    if len(words) <= max_words:
        return value.strip()
    return " ".join(words[:max_words]).rstrip(" ,.;:") + "…"

def generate_weekly_pulse(result: dict, pulse_date: str | None = None) -> str:
    """Generate a concise internal update using only supplied analysis results."""
    pulse_date = pulse_date or date.today().isoformat()
    themes = (result.get("top_three_themes") or result.get("themes") or [])[:3]
    quotes = (result.get("quotes") or [])[:3]
    total = result.get("total_reviews", 0)

    lines = [
        f"# Groww Weekly Product Pulse — {pulse_date}",
        f"**Coverage:** {total} public feedback records analysed.",
        "",
        "## Top themes",
    ]
    for item in themes:
        lines.append(f"- {item['theme']}: {item['count']} reviews ({item['share_pct']}%).")

    lines += ["", "## Customer voice"]
    for item in quotes:
        quote = _short_quote(item.get("quote", ""))
        source = item.get("source") or "Source not recorded"
        review_date = item.get("review_date") or "date not recorded"
        review_id = item.get("review_id") or "ID not recorded"
        lines.append(f"- “{quote}” ({source}, {review_date}; {review_id}).")

    top_theme = themes[0]["theme"] if themes else ""
    observations = {
        "App experience and customer support": (
            "App experience and support is the largest classified theme. Reviews report "
            "reliability, access, transaction-status and support-resolution concerns; "
            "these are customer reports, not independently verified incidents."
        ),
        "Fees and charges": (
            "Fees and charges is the largest classified theme. Validate the exact charge "
            "and disclosure context before concluding that a fee is incorrect."
        ),
        "Investment information and performance": (
            "Investment information is the largest classified theme. Validate reported "
            "display and allocation concerns against transaction records and official data."
        ),
        "Withdrawals and redemptions": (
            "Withdrawal and redemption concerns lead the classified feedback. Validate "
            "reported delays and settlement questions against operational data."
        ),
    }
    observation = observations.get(
        top_theme,
        "The leading theme is an investigation signal; validate individual cases before "
        "concluding that feedback represents a confirmed product defect."
    )
    lines += ["", "## Key observation", observation, "", "## Product actions"]
    actions = ACTION_LIBRARY.get(top_theme, [
        "Validate the highest-volume customer cases and the underlying journey.",
        "Assign product and operational owners and quantify customer impact.",
        "Improve customer-facing information where the evidence supports a change.",
    ])
    lines.extend(f"- {action}" for action in actions[:3])

    note = "\n".join(lines)
    # The content is intentionally concise; fail loudly rather than silently cutting a sentence.
    if _word_count(note) > 250:
        raise ValueError(
            f"Product Pulse is {_word_count(note)} words. Shorten source quotes or sections; "
            "the generator will not truncate a sentence."
        )
    return note
