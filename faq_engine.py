import json
import re
from datetime import date
from pathlib import Path

FACTS_PATH = Path(__file__).parent / "data" / "facts.json"
SCHEMES = [
    "HDFC Nifty 50 Index Fund",
    "HDFC Flexi Cap Fund",
    "HDFC ELSS Tax Saver Fund",
    "HDFC Mid Cap Fund",
]
ADVICE_PHRASES = [
    "should i buy", "should i sell", "should i hold", "should i switch",
    "recommend a fund", "which fund should", "best fund for me",
    "what should i invest", "should i invest", "is this fund right for me",
    "portfolio advice", "investment advice", "where should i invest",
]
PII_PATTERNS = [
    r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", r"\b\d{12}\b", r"\b\d{10}\b",
    r"\bOTP\b", r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b",
]
TOPICS = {
    "exit load": ["exit load", "exit", "redeem", "redemption", "withdraw", "switch"],
    "minimum SIP": ["minimum sip", "minimum", "sip", "systematic investment", "installment", "instalment"],
    "lock-in": ["lock-in", "lock in", "lock", "elss"],
    "riskometer": ["riskometer", "risk level", "risk"],
    "benchmark": ["benchmark", "benchmarked", "tracks", "tracked", "index"],
    "expense ratio": ["expense ratio", "expense", "ter", "total expense"],
    "scheme type": ["scheme type", "type", "category", "flexi cap"],
    "statement download": ["statement", "account statement", "capital gains", "tax statement", "download"],
}

def load_facts():
    with open(FACTS_PATH, encoding="utf-8") as f:
        return json.load(f)

def format_answer(message, source_url="https://investor.sebi.gov.in/", updated=None):
    return f"{message}\n\nSource: {source_url}\n\nLast updated from sources: {updated or date.today().isoformat()}"

def answer_question(question, facts=None):
    q = question.strip()
    low = q.lower()
    if not q:
        return format_answer("Please enter a general factual question.")

    if any(re.search(p, q, re.I) for p in PII_PATTERNS):
        return format_answer(
            "Please do not enter personal information such as PAN, Aadhaar, account numbers, OTPs, email addresses, or phone numbers. This assistant does not need personal information.",
            "https://investor.sebi.gov.in/"
        )

    if any(p in low for p in ADVICE_PHRASES):
        return format_answer(
            "I can share factual scheme information, but I can’t recommend whether you should buy, sell, hold, or switch an investment. Please consult a qualified financial adviser for personalised advice.",
            "https://investor.sebi.gov.in/"
        )

    if any(p in low for p in ["what schemes are covered", "which schemes are covered", "schemes covered", "what schemes does this assistant cover", "list the schemes", "which funds are covered"]):
        return format_answer(
            "This prototype covers HDFC Nifty 50 Index Fund, HDFC Flexi Cap Fund, HDFC ELSS Tax Saver Fund, and HDFC Mid Cap Fund. The available facts vary by scheme.",
            "https://www.hdfcfund.com/explore/mutual-funds"
        )

    facts = facts if facts is not None else load_facts()
    named = [s for s in SCHEMES if s.lower() in low]
    if not named and any(t in low for t in ["statement", "capital gains", "tax statement"]):
        named = ["HDFC Mutual Fund"]
    if not named:
        return format_answer("I couldn’t verify that fact from the approved source collection. Please check the official HDFC Mutual Fund scheme page or latest Scheme Information Document.", "https://www.hdfcfund.com/explore/mutual-funds")

    topic = None
    for candidate in ["exit load", "minimum SIP", "lock-in", "riskometer", "benchmark", "expense ratio", "scheme type", "statement download"]:
        terms = TOPICS[candidate]
        if any(t in low for t in terms):
            if candidate == "scheme type" and any(t in low for t in ["exit", "redeem", "redemption", "benchmark", "index"]):
                continue
            topic = candidate
            break
    if topic is None:
        return format_answer("I couldn’t identify a supported FAQ topic. Try exit load, minimum SIP, lock-in, riskometer, benchmark, scheme type, or statement services.", "https://www.hdfcfund.com/explore/mutual-funds")

    matches = [f for f in facts if f.get("scheme", "").lower() in [s.lower() for s in named] and f.get("topic", "").lower() == topic.lower()]
    if not matches:
        return format_answer("I couldn’t verify that fact from the approved source collection. Please check the official HDFC Mutual Fund scheme page or latest Scheme Information Document.", "https://www.hdfcfund.com/explore/mutual-funds")
    fact = matches[0]
    return format_answer(fact["answer"], fact["source_url"], fact.get("checked_on"))
