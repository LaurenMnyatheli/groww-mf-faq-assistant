# Groww Mutual Fund FAQ Assistant & Customer Feedback Intelligence

A Streamlit-based AI prototype built as part of the NextLeap Product Management programme. The project combines a facts-only Mutual Fund FAQ Assistant with a customer feedback intelligence workflow that turns public customer reviews into structured product insights and approval-gated internal communications.

## Live Application

- **Streamlit prototype:** https://laurenmnyatheli-groww-mf-faq-assistant-app-3ayiz5.streamlit.app/
- **GitHub repository:** https://github.com/LaurenMnyatheli/groww-mf-faq-assistant

The application has two main experiences:

1. **Mutual Fund FAQ Assistant** – provides factual mutual fund information using its curated knowledge base.
2. **Customer Feedback Intelligence** – analyses public customer reviews, generates a weekly product pulse, retrieves official fee information and prepares an internal update for human approval.

---

## 1. Project Objectives

The Customer Feedback Intelligence workflow was designed to address three product challenges:

- Customer feedback is spread across public review platforms and can be difficult to consolidate.
- Product teams need a repeatable way to identify customer pain points and turn feedback into actionable insights.
- Frequently misunderstood product fees require clear, consistent explanations grounded in official information.

The workflow transforms raw public reviews into structured insights and reusable customer-facing explanations, while retaining human oversight before distribution.

## 2. Key Features

### A. Customer Review Analysis

- Upload a public customer reviews CSV file.
- Clean and deduplicate non-empty review records.
- Classify reviews into themes using transparent keyword-based rules.
- Display theme counts and supporting customer excerpts.
- Identify potential fee-related issues for further investigation.
- Preserve review IDs, dates and source information where available.

### B. Weekly Product Pulse

Generates a structured internal product update containing:

- Review coverage and analysis period.
- Leading customer feedback themes.
- Supporting customer excerpts.
- Key observations.
- Recommended product, engineering and support actions.

The pulse is generated from the review analysis and is intended for human review before internal distribution.

### C. RAG Fee Explainer

The fee explainer uses a curated corpus of official Groww, SEBI and AMFI source material.

It:

- Retrieves relevant source excerpts using lexical token-overlap matching.
- Produces a concise, reusable customer explanation.
- Includes up to six explanation bullets.
- Displays official source links.
- Includes a last-checked date.

The current investigation topic is **Expense Ratio vs Total Expense Ratio (TER)**.

The uploaded review dataset does not establish a recurring fee misunderstanding. The expense-ratio topic is therefore treated as an investigation candidate, not a confirmed recurring customer issue.

### D. Human Approval and Distribution

The workflow includes an explicit approval gate before information is distributed.

After reviewing the product pulse and fee explanation, an authorised user must:

1. Open the information preview.
2. Review the proposed content.
3. Tick the approval checkbox.
4. Click **Approve and send to Make**.

Only after this action does the application submit the approved payload to the Make webhook.

### E. Make.com Automation

The approved payload triggers a Make scenario containing three modules:

1. **Custom Webhook:** Receives the approved structured payload.
2. **Google Docs:** Appends the weekly product pulse and fee explanation to an existing document.
3. **Gmail:** Creates an email draft for internal review.

The workflow creates a Gmail draft. It does not automatically send an email.

---

## 3. Workflow Architecture

```text
Public Customer Reviews (CSV)
             |
             v
     Review Analysis
             |
             v
   Theme Classification
             |
             v
    Weekly Product Pulse
             |
             v
    Fee Issue Investigation
             |
             v
       RAG Retrieval
             |
             v
    Customer Fee Explanation
             |
             v
      Human Approval Gate
             |
             v
       Make Webhook
          /       \
         v         v
   Google Docs   Gmail Draft
    Append       Create Draft
```

## 4. Technology Stack

| Component | Technology |
|---|---|
| Application interface | Streamlit |
| Data processing | Python, Pandas |
| Review analysis | Transparent keyword-based classification |
| Product pulse | Python-based generation |
| Fee knowledge retrieval | Lexical token-overlap retrieval |
| Workflow automation | Make.com |
| Document distribution | Google Docs |
| Email distribution | Gmail |
| Version control | GitHub |
| Deployment | Streamlit Community Cloud |

## 5. Repository Structure

```text
groww-mf-faq-assistant/
│
├── app.py
├── faq_engine.py
├── feedback_intelligence.py
├── requirements.txt
├── README.md
├── sample_qa.md
│
├── data/
│   └── fee_knowledge.json
│
├── modules/
│   ├── fee_rag.py
│   ├── make_approval.py
│   ├── product_pulse.py
│   └── review_analyser.py
│
├── tests/
│
└── groww_public_customer_reviews_sample.csv
```

*The repository may contain additional supporting files.*

## 6. Running the Application Locally

### Prerequisites

- Python 3.10 or later
- Git
- A Make.com account for the distribution workflow

### Step 1: Clone the repository

```bash
git clone https://github.com/LaurenMnyatheli/groww-mf-faq-assistant.git

cd groww-mf-faq-assistant
```

### Step 2: Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Mac/Linux**
```bash
source venv/bin/activate
```

**Windows**
```bash
venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure secrets

The approval workflow requires the following Streamlit secrets:

```toml
MAKE_WEBHOOK_URL = "your_make_webhook_url"
MAKE_WEBHOOK_API_KEY = "your_make_api_key"
```

Add these values through Streamlit App Settings → Secrets.

Do not commit API keys, webhook credentials or other secrets to GitHub.

### Step 5: Run the application

```bash
streamlit run app.py
```

Open the local URL provided by Streamlit.

---

## 7. Sample Customer Feedback Analysis

The prototype was tested using a public customer review dataset.

The tested dataset contained **24 non-empty, deduplicated review records**.

The initial analysis identified the following themes:

| Theme | Reviews | Share |
|---|---:|---:|
| App experience and customer support | 12 | 50.0% |
| Fees and charges | 6 | 25.0% |
| Investment information and performance | 4 | 16.7% |
| Withdrawals and redemptions | 2 | 8.3% |

### Key Observation

App experience and customer support represented the largest classified theme.

Customer reviews reported concerns relating to reliability, access, transaction status and support resolution.

These are customer-reported experiences and have not been independently verified as platform incidents.

### Recommended Product Actions

- **Engineering:** Investigate reported reliability, access and transaction-status concerns against internal incident data.
- **Customer Support:** Review escalation paths, response times and repeat-contact drivers.
- **Product:** Improve the clarity of transaction and account-status messages.

---

## 8. Fee Explanation: Expense Ratio vs TER

The current RAG demonstration investigates the distinction between Base Expense Ratio (BER) and Total Expense Ratio (TER).

The explanation is retrieved from a curated official-source corpus and is intended as a draft for review.

Official reference sources:

- [Groww – BER instead of TER: What changed and why](https://groww.in/updates/groww-now-shows-base-expense-ratio-instead-of-total-expense-ratio)
- [SEBI – Mutual Fund Master Circular](https://www.sebi.gov.in/)
- [AMFI – Total Expense Ratio disclosures](https://www.amfiindia.com/ter-of-mf-schemes)

The fee topic is an investigation candidate. The available review sample does not establish that this is a recurring customer misunderstanding.

---

## 9. Human-in-the-Loop Controls

Human approval is a core part of the workflow.

The application does not distribute the generated update automatically.

The user must explicitly approve the content before the webhook is called.

The downstream workflow is restricted to:

- Appending content to Google Docs.
- Creating an email draft in Gmail.

**Automatic email sending is not enabled.**

This ensures that generated insights and customer explanations can be checked before being shared.

---

## 10. Known Limitations and Future Improvements

The current prototype has several limitations:

1. **Review classification:** Uses transparent keyword-based rules rather than semantic or LLM-based clustering.
2. **Dataset coverage:** Analysis is limited to the reviews uploaded by the user and should not be treated as representative of all Groww customers.
3. **Fee issue detection:** The current sample does not establish a recurring fee misunderstanding.
4. **RAG retrieval:** Uses lexical token-overlap matching over a small curated corpus rather than a vector database or semantic retrieval model.
5. **Source validation:** Official sources and fee explanations require periodic review to ensure they remain current.
6. **Distribution:** Google Docs append and Gmail draft creation are automated, but final communication remains subject to human review.

### Potential Next Iterations

- Introduce semantic review clustering and LLM-assisted theme summarisation.
- Expand the review dataset across more public sources and longer periods.
- Add sentiment and severity classification.
- Introduce trend comparisons between reporting periods.
- Expand the official fee knowledge base.
- Add automated source freshness checks.
- Add approval audit logs and duplicate-submission protection.

---

## 11. Project Outcome

The prototype demonstrates an end-to-end workflow that connects customer feedback analysis, product insight generation, source-grounded explanations and human-approved communication distribution.

It demonstrates how AI-assisted workflows can reduce manual effort for product teams while preserving transparency, source traceability and human control.

**The central principle:** AI helps organise and prepare the work; a human remains responsible for reviewing and approving what gets shared.
