# Groww Mutual Fund FAQ Assistant

A beginner-friendly educational prototype for factual questions about selected HDFC Mutual Fund schemes.

## Scope and safeguards
- Facts-only answers from a small curated JSON collection.
- One official source URL and a `Last updated from sources: YYYY-MM-DD` line for every answer.
- Refuses personalised buy/sell/hold/switch advice.
- Warns users not to enter PAN, Aadhaar, account numbers, OTPs, email addresses, or phone numbers.
- Does not calculate or compare returns, predict performance, connect to customer accounts, or call a hosted LLM.

## Schemes covered
- HDFC Nifty 50 Index Fund
- HDFC Flexi Cap Fund
- HDFC ELSS Tax Saver Fund
- HDFC Mid Cap Fund

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run `python -m pip install -r requirements.txt`.
4. Run `streamlit run app.py`.

## Deploy on Streamlit Community Cloud
1. Upload all files and folders in this project to the root of your GitHub repository.
2. In Streamlit Community Cloud, select the repository and choose `app.py` as the main file.
3. Ensure `app.py`, `faq_engine.py`, `requirements.txt`, and the `data` folder are all committed.
4. If the page is blank, check app logs and confirm the main file is `app.py`.

## Update facts safely
Only update `data/facts.json` after checking the latest official HDFC scheme page or Scheme Information Document. Update `checked_on` only when the source was actually reviewed. Keep the source inventory in `data/sources.csv` aligned with the facts.

## Accuracy note
Some facts in this starter dataset were carried forward from earlier draft notes and have not been independently re-verified here. Treat all figures and URLs as unverified until you check the current official documents. Do not present this as an investment-advice tool.

## Files
- `app.py`: Streamlit interface
- `faq_engine.py`: matching, safety checks, and answer formatting
- `data/facts.json`: starter fact collection
- `data/sources.csv`: source inventory
- `tests/test_faq.py`: basic automated checks
- `sample_qa.md`: example Q&A and expected safety behaviour
