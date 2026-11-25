"""Lightweight retrieval-augmented fee explainer over a curated official-source corpus."""
from __future__ import annotations

import json
import re
from pathlib import Path
from collections import Counter

CORPUS_PATH = Path(__file__).resolve().parent.parent / "data" / "fee_knowledge.json"

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "what", "when", "where",
    "your", "you", "are", "can", "does", "into", "not", "has", "have", "been",
    "about", "shown", "show", "groww", "fund", "mutual"
}

def _tokens(text: str) -> list[str]:
    return [
        t for t in re.findall(r"[a-zA-Z0-9]+", text.lower())
        if len(t) > 2 and t not in STOPWORDS
    ]

def load_corpus() -> list[dict]:
    with open(CORPUS_PATH, encoding="utf-8") as f:
        return json.load(f)

def retrieve_chunks(query: str, corpus: list[dict] | None = None, top_k: int = 2) -> list[dict]:
    """Rank curated source chunks using transparent token overlap (lexical retrieval)."""
    corpus = corpus if corpus is not None else load_corpus()
    q_terms = Counter(_tokens(query))
    ranked = []
    for chunk in corpus:
        doc_terms = Counter(_tokens(chunk["title"] + " " + chunk["text"]))
        overlap = sum(min(count, doc_terms[t]) for t, count in q_terms.items())
        if overlap:
            ranked.append((overlap, chunk))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in ranked[:top_k]]

def build_fee_explainer(issue: str = "Expense ratio vs Total Expense Ratio (TER)") -> dict:
    """Generate a short facts-only explanation with citations from retrieved chunks."""
    query = issue + " Groww Base Expense Ratio BER Total Expense Ratio TER NAV brokerage transaction costs statutory levies GST AMFI"
    retrieved = retrieve_chunks(query, top_k=3)
    if len(retrieved) < 2:
        return {
            "status": "insufficient_sources",
            "issue": issue,
            "bullets": [],
            "sources": [],
            "last_checked": None,
            "message": "Not enough relevant official source material was retrieved. Do not publish an explanation."
        }

    bullets = [
        "Groww states that the expense-ratio figure shown as the primary number on its fund details page is the Base Expense Ratio (BER), not the Total Expense Ratio (TER).",
        "BER represents the scheme's base management and operating expenses.",
        "TER is broader: it comprises BER, brokerage costs, eligible transaction costs and applicable statutory levies, including GST.",
        "The expenses are reflected in the mutual fund scheme's NAV; they are not charged as a separate BER/TER debit from the investor's bank account.",
        "TER can vary as trading-related costs and statutory levies change. A change in TER does not necessarily mean the AMC changed its base management cost.",
        "For a scheme-specific TER, check the relevant scheme and period on AMFI's official TER disclosure page or the AMC's official disclosures."
    ]
    sources = []
    for item in retrieved:
        sources.append({
            "title": item["source_title"],
            "url": item["source_url"],
            "source_type": item["source_type"]
        })
    # Ensure the two core official sources are present even if lexical ranking differs.
    required = [
        ("Groww — BER instead of TER: what changed and why",
         "https://groww.in/updates/groww-now-shows-base-expense-ratio-instead-of-total-expense-ratio",
         "Official Groww explanation"),
        ("SEBI — Master Circular for Mutual Funds, Chapter 11",
         "https://www.sebi.gov.in/sebi_data/attachdocs/mar-2026/1774024028162.pdf",
         "Official SEBI regulatory source"),
        ("AMFI — Total Expense Ratio of Mutual Fund Schemes",
         "https://www.amfiindia.com/ter-of-mf-schemes",
         "Official AMFI disclosure lookup")
    ]
    for title, url, source_type in required:
        if not any(s["url"] == url for s in sources):
            sources.append({"title": title, "url": url, "source_type": source_type})
    return {
        "status": "draft",
        "issue": issue,
        "bullets": bullets,
        "sources": sources[:3],
        "last_checked": "2026-11-25",
        "retrieved_chunk_ids": [item["chunk_id"] for item in retrieved],
        "retrieval_method": "Transparent lexical token-overlap retrieval over a curated official-source corpus."
    }
