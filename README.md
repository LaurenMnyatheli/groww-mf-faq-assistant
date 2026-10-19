# Groww Mutual Fund FAQ Assistant

A beginner-friendly prototype for the NextLeap milestone **AI System Design, LLMs & Prompt Engineering**.

## What it does
- Answers a small set of factual questions about selected HDFC Mutual Fund schemes.
- Uses a curated local facts collection and keyword-based retrieval.
- Shows one official source URL with every answer.
- Refuses personalised buy/sell/hold/switch recommendations.
- Warns users not to enter personal information.
- Includes a documented system prompt for a future LLM integration.

> **Important:** This is a learning prototype, not a financial product. Facts and URLs must be checked against the latest official documents before submission. It is not investment advice.

## Scope
- **Selected product:** Groww
- **AMC / corpus owner:** HDFC Mutual Fund
- **Schemes:** HDFC ELSS Tax Saver Fund, HDFC Nifty 50 Index Fund, HDFC Mid Cap Fund, HDFC Flexi Cap Fund
- **Approved source types:** AMC scheme pages, factsheets and statement pages, plus SEBI and AMFI official public pages.
- **Out of scope:** personalised recommendations, performance calculations/comparisons, account lookups, and any handling of personal data.

## How retrieval works
1. The user enters a question.
2. A safety check looks for advice requests and common PII patterns.
3. Keyword retrieval ranks facts in `data/facts.json`.
4. If a supported fact is found, the app displays the stored answer and its official source URL.
5. If the fact is not in the small knowledge base, the app says it cannot verify the answer.

This starter version is deliberately deterministic so it can run without a paid API key. `SYSTEM_PROMPT` in `app.py` documents the instructions that should be used if an LLM is added. Do not describe this starter version as an LLM-powered answer generator; it is a retrieval-based FAQ prototype with an LLM system-prompt design artifact.

## Setup on your computer or Google Colab
### Option A: run locally
1. Install Python 3.10 or newer.
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the app:
   ```bash
   streamlit run app.py
   ```
6. Open the local URL Streamlit shows, usually `http://localhost:8501`.

### Option B: Google Colab
Colab is suitable for experimenting with Python, but it is not the easiest way to host a persistent Streamlit website. Use Streamlit Community Cloud for the final hosted app.

## Deploy on Streamlit Community Cloud
1. Push the project to a GitHub repository.
2. Sign in at https://share.streamlit.io/ using GitHub.
3. Choose **Create app**, select the repository and branch, and set the main file path to `app.py`.
4. Deploy and wait for the build to finish.
5. Open the generated public app URL in a private/incognito window to check that it loads.
6. Submit that URL as the working prototype link.

## Repository contents
- `app.py`: Streamlit interface, safety checks and retrieval.
- `data/facts.json`: curated answer facts and citation URLs.
- `data/sources.csv`: source inventory (20 rows; includes a repeated scheme URL for field mapping).
- `sample_qa.md`: sample queries and expected behaviour.
- `tests/test_faq.py`: basic safety and retrieval tests.
- `requirements.txt`: Python dependencies.
- `.gitignore`: excludes secrets and local environments.

## Privacy and safety
- Do not ask for or store PAN, Aadhaar, account numbers, OTPs, email addresses or phone numbers.
- Never commit API keys or secrets to GitHub.
- The prototype does not connect to Groww accounts and does not store chat history.
- The app blocks common PII patterns, but pattern matching is not perfect; do not enter personal information.

## Known limitations
- The knowledge base is small and manually curated.
- The app does not automatically crawl or refresh official websites.
- `checked_on` is the date the starter facts were assembled, not a guarantee that each page was independently revalidated on that date.
- Scheme values can change and may differ by plan, option or transaction type. Always verify the latest SID/KIM/factsheet.
- The current app uses deterministic retrieval, not a live LLM. To meet a strict requirement for an LLM-powered RAG prototype, add a hosted LLM integration and test grounding before claiming that capability.
- Source URLs are starter candidates; check all 20 URLs and replace any that redirect or are no longer current.

## Disclaimer used in the UI
“Facts-only. No investment advice. Do not enter PAN, Aadhaar, account numbers, OTPs, email addresses, or phone numbers.”
