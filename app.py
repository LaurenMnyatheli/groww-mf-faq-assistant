import streamlit as st
from faq_engine import answer_question

st.set_page_config(page_title="Groww Mutual Fund FAQ Assistant", page_icon="📘", layout="centered")
st.title("📘 Groww Mutual Fund FAQ Assistant")
st.caption("Educational prototype for factual questions about selected HDFC Mutual Fund schemes.")
st.info("Facts-only. No investment advice. Do not enter PAN, Aadhaar, account numbers, OTPs, email addresses, or phone numbers.")
st.write("Ask about exit load, minimum SIP, lock-in, riskometer, benchmark, scheme type, or statement services.")

examples = [
    "What is the lock-in period for HDFC ELSS Tax Saver Fund?",
    "What is the exit load for HDFC Nifty 50 Index Fund?",
    "What is the benchmark for HDFC Mid Cap Fund?",
    "What schemes are covered by this assistant?",
]
for start in range(0, len(examples), 2):
    cols = st.columns(2)
    for col, example in zip(cols, examples[start:start + 2]):
        if col.button(example, use_container_width=True):
            st.session_state["question"] = example

with st.form("question_form"):
    question = st.text_input("Your question", key="question", placeholder="e.g. What is the exit load for HDFC Flexi Cap Fund?")
    submitted = st.form_submit_button("Get answer", type="primary", use_container_width=True)
if submitted:
    st.markdown("### Answer")
    st.write(answer_question(question))

with st.expander("About this prototype"):
    st.write("This version uses deterministic matching over a small curated JSON collection. It does not connect to customer accounts or a hosted LLM.")
    st.warning("The starter facts and URLs must be checked against current official scheme documents before final submission.")
