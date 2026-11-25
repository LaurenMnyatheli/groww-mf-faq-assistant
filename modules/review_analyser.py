"""Transparent baseline review analyser for the Groww NextLeap prototype.

This version uses explainable keyword rules, not an LLM. It does not invent
reviews or quotes. A recurring fee issue is reported only when at least two
distinct reviews mention the same fee topic.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

import pandas as pd

THEMES = {
    "Fees and charges": [
        "exit load", "expense ratio", "ter", "charge", "charges", "fee", "fees",
        "deduction", "deducted", "commission", "tax", "stamp duty",
    ],
    "Withdrawals and redemptions": [
        "withdraw", "withdrawal", "redeem", "redemption", "refund",
        "sell", "settlement", "credited", "credit",
    ],
    "Transactions and payments": [
        "payment", "paid", "deposit", "add money", "lumpsum", "lump sum",
        "sip", "mandate", "bank", "failed", "processing",
    ],
    "Investment information and performance": [
        "nav", "returns", "return", "performance", "loss", "profit",
        "portfolio", "invested value", "scheme", "fund",
    ],
    "App experience and customer support": [
        "app", "login", "server", "error", "crash", "support", "customer care",
        "blocked", "response", "resolution", "information",
    ],
}

FEE_PATTERNS = {
    "Exit load confusion": [
        r"\bexit[\s-]?load\b", r"\bexit charge\b",
        r"\bdeduct(?:ed|ion)?\b.{0,50}\b(redemption|redeem|withdraw|sell)\b",
        r"\b(redemption|redeem|withdraw|sell)\b.{0,50}\b(charge|fee|deduct(?:ed|ion)?)\b",
    ],
    "Expense ratio confusion": [
        r"\bexpense ratio\b", r"\bTER\b", r"\btotal expense ratio\b",
    ],
    "Other fee or charge confusion": [
        r"\b(hidden|unexpected|extra)\b.{0,30}\b(fee|fees|charge|charges)\b",
        r"\b(fee|fees|charge|charges)\b.{0,30}\b(hidden|unexpected|extra)\b",
    ],
}


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    required = {"review_text"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError("CSV is missing required column(s): " + ", ".join(sorted(missing)))
    for col in ["review_id", "review_date", "rating", "source", "product_area", "source_url"]:
        if col not in df.columns:
            df[col] = ""
    df["review_text"] = df["review_text"].fillna("").astype(str).str.strip()
    df = df[df["review_text"].ne("")]
    df = df.drop_duplicates(subset=["review_text"])
    return df


def analyse_reviews(raw_df: pd.DataFrame) -> dict[str, Any]:
    """Cluster feedback into up to five themes and identify fee signals."""
    df = _normalise_columns(raw_df)
    if df.empty:
        raise ValueError("No non-empty review_text rows were found.")

    theme_counts: Counter[str] = Counter()
    theme_rows: dict[str, list[int]] = {name: [] for name in THEMES}

    for idx, row in df.iterrows():
        text = row["review_text"].lower()
        scores = {
            theme: sum(1 for term in terms if re.search(r"\b" + re.escape(term) + r"\b", text))
            for theme, terms in THEMES.items()
        }
        # Assign a review to its strongest theme only, avoiding double-counting.
        best_theme, best_score = max(scores.items(), key=lambda item: item[1])
        if best_score > 0:
            theme_counts[best_theme] += 1
            theme_rows[best_theme].append(idx)

    top_themes = [
        {"theme": theme, "count": count, "share_pct": round(count / len(df) * 100, 1)}
        for theme, count in theme_counts.most_common(5)
    ]

    fee_hits: list[dict[str, Any]] = []
    for fee_name, patterns in FEE_PATTERNS.items():
        matched = df[df["review_text"].str.lower().apply(
            lambda text: any(re.search(pattern, text, re.I) for pattern in patterns)
        )]
        if not matched.empty:
            fee_hits.append({
                "issue": fee_name,
                "count": int(len(matched)),
                "review_ids": matched["review_id"].astype(str).tolist(),
                "quotes": matched["review_text"].head(3).tolist(),
            })

    fee_hits.sort(key=lambda item: item["count"], reverse=True)
    recurring_fee_issue = fee_hits[0] if fee_hits and fee_hits[0]["count"] >= 2 else None

    # Select up to three verbatim review excerpts from the most represented themes.
    quote_rows = []
    for theme, _ in theme_counts.most_common():
        for idx in theme_rows[theme]:
            row = df.loc[idx]
            quote_rows.append({
                "theme": theme,
                "review_id": str(row["review_id"]),
                "review_date": str(row["review_date"]),
                "source": str(row["source"]),
                "quote": str(row["review_text"]),
                "source_url": str(row["source_url"]),
            })
            if len(quote_rows) == 3:
                break
        if len(quote_rows) == 3:
            break

    return {
        "total_reviews": int(len(df)),
        "themes": top_themes,
        "top_three_themes": top_themes[:3],
        "quotes": quote_rows,
        "fee_issue_candidates": fee_hits,
        "recurring_fee_issue": recurring_fee_issue,
        "fee_finding_note": (
            "A recurring fee-related issue was detected in at least two distinct reviews."
            if recurring_fee_issue else
            "The current dataset does not establish a recurring fee misunderstanding. "
            "Collect more relevant reviews before selecting a fee issue."
        ),
        "method_note": (
            "Initial transparent keyword-based baseline. Theme labels and fee signals "
            "must be reviewed by a person; this is not yet LLM-based clustering."
        ),
    }


def to_markdown_report(result: dict[str, Any]) -> str:
    lines = [
        "# Groww Customer Review Intelligence",
        f"Reviews analysed: {result['total_reviews']}",
        "",
        "## Themes",
    ]
    if result["themes"]:
        for item in result["themes"]:
            lines.append(f"- **{item['theme']}**: {item['count']} reviews ({item['share_pct']}%)")
    else:
        lines.append("- No themes matched the current classifier.")
    lines += ["", "## Verbatim customer excerpts"]
    for item in result["quotes"]:
        lines.append(f"- “{item['quote']}” — {item['source']}, {item['review_date']} ({item['review_id']})")
    lines += ["", "## Fee-related signal", result["fee_finding_note"]]
    if result["recurring_fee_issue"]:
        fee = result["recurring_fee_issue"]
        lines.append(f"Candidate: **{fee['issue']}** ({fee['count']} reviews)")
    lines += ["", "## Method", result["method_note"]]
    return "\n".join(lines)
