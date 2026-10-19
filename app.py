import streamlit as st
from faq_engine import answer_question

st.set_page_config(
    page_title="Groww Mutual Fund FAQ Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
:root { --purple:#6d45e8; --ink:#191547; --muted:#625f7b; --line:#e8e5f2; }
.block-container {max-width: 1120px; padding-top: 1.4rem; padding-bottom: 2.5rem;}
#MainMenu, footer {visibility:hidden;}
header[data-testid="stHeader"] {background:transparent;}
.brand {display:flex;align-items:center;gap:14px;margin-bottom:1.3rem;}
.brand-icon {width:54px;height:54px;border-radius:16px;background:#eee8ff;display:flex;align-items:center;justify-content:center;font-size:27px;}
.brand-name {font-size:1.65rem;font-weight:800;color:var(--ink);line-height:1.15;}
.brand-sub {font-size:1rem;color:#77719e;margin-top:3px;}
.trust {margin-left:auto;background:#f5f1ff;color:#332078;border-radius:14px;padding:12px 16px;font-weight:700;font-size:.9rem;}
.hero {background:linear-gradient(115deg,#f2edff 0%,#faf8ff 70%,#eee8ff 100%);border:1px solid #eee7ff;border-radius:22px;padding:30px 32px;margin:0 0 26px 0;}
.eyebrow {text-transform:uppercase;letter-spacing:2px;font-size:.78rem;font-weight:800;color:#7550e9;margin-bottom:9px;}
.hero h1 {font-size:2.35rem;line-height:1.12;color:var(--ink);margin:0 0 12px 0;}
.hero p {font-size:1.06rem;color:#383260;max-width:720px;margin-bottom:16px;}
.notice {background:#e7ddff;border-radius:12px;padding:13px 15px;color:#31225f;font-size:.9rem;max-width:780px;}
.section-heading {font-size:1.35rem;font-weight:800;color:var(--ink);margin:0 0 3px 0;}
.section-sub {color:var(--muted);margin-bottom:14px;}
div[data-testid="stForm"] {border:1px solid #ddd8ec;border-radius:16px;padding:14px 16px;background:white;}
.stButton > button {border-radius:12px;border:1px solid #e7e2f2;background:#fff;color:#25204d;font-weight:650;min-height:56px;white-space:normal;}
.stButton > button:hover {border-color:#9a80f0;color:#5a36d6;background:#faf8ff;}
.stFormSubmitButton > button {background:var(--purple)!important;color:white!important;border:0!important;min-height:48px;}
.answer-card {border:1px solid #b8f0dd;background:linear-gradient(110deg,#f2fff9,#fff);border-radius:17px;padding:22px 24px;margin-top:20px;color:#242047;}
.answer-title {font-size:1.12rem;font-weight:800;margin-bottom:10px;}
.answer-text {font-size:1.02rem;line-height:1.65;white-space:pre-wrap;}
.answer-meta {border-top:1px solid #d9eee6;margin-top:17px;padding-top:12px;font-size:.9rem;color:#514b70;overflow-wrap:anywhere;}
.footer-note {background:#f8f1fb;border-radius:14px;padding:16px 20px;margin-top:22px;color:#51466b;font-size:.9rem;}
@media(max-width:700px){.hero{padding:22px 18px}.hero h1{font-size:1.8rem}.brand-name{font-size:1.25rem}.trust{display:none}.block-container{padding-left:1rem;padding-right:1rem}}
</style>
""", unsafe_allow_html=True)

st.markdown('''
<div class="brand">
  <div class="brand-icon">📊</div>
  <div><div class="brand-name">Groww</div><div class="brand-sub">Mutual Fund FAQ Assistant</div></div>
  <div class="trust">🛡️ &nbsp; Trusted information<br><span style="font-weight:400">Facts from official sources</span></div>
</div>
<div class="hero">
  <div class="eyebrow">Welcome to the</div>
  <h1>Groww Mutual Fund<br>FAQ Assistant</h1>
  <p>Get quick, factual answers about selected HDFC mutual fund schemes, including fund details, fees, tax information and more.</p>
  <div class="notice"><b>ⓘ &nbsp; This assistant provides factual information only.</b><br>It does not offer personalised investment advice. Please consult a qualified financial adviser for investment decisions.</div>
</div>
''', unsafe_allow_html=True)

st.markdown('<div class="section-heading">Try an example question</div><div class="section-sub">Choose a question below or type your own.</div>', unsafe_allow_html=True)
examples = [
    ("📄  Fund details", ["What schemes are covered by this assistant?", "What is the benchmark for HDFC Mid Cap Fund?"]),
    ("％  Fees and charges", ["What is the exit load for HDFC Nifty 50 Index Fund?", "What is the lock-in period for HDFC ELSS Tax Saver Fund?"]),
    ("🪙  Tax information", ["What is the lock-in period for HDFC ELSS Tax Saver Fund?"]),
    ("🛡️  Investment safety", ["Should I buy HDFC Mid Cap Fund?"]),
]
cols = st.columns(4)
for col, (heading, questions) in zip(cols, examples):
    with col:
        st.markdown(f"**{heading}**")
        for i, example in enumerate(questions):
            if st.button(example, key=f"example_{heading}_{i}", use_container_width=True):
                st.session_state["question"] = example
                st.session_state["run_answer"] = True

with st.form("question_form", clear_on_submit=False):
    question = st.text_input("Your question", key="question", placeholder="Type your question about the supported funds…", label_visibility="collapsed")
    submitted = st.form_submit_button("➤  Get answer", type="primary", use_container_width=True)

if submitted:
    st.session_state["run_answer"] = True

if st.session_state.get("run_answer", False):
    result = answer_question(st.session_state.get("question", ""))
    parts = result.split("\n\n")
    answer = parts[0] if parts else result
    source = next((p.removeprefix("Source: ") for p in parts if p.startswith("Source: ")), "")
    updated = next((p for p in parts if p.startswith("Last updated from sources:")), "")
    st.markdown('<div class="answer-card"><div class="answer-title">✓ &nbsp; Answer</div><div class="answer-text">' + answer.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + '</div></div>', unsafe_allow_html=True)
    meta_cols = st.columns([3, 2])
    with meta_cols[0]:
        if source:
            st.markdown(f"🔗 **Source:** [{source}]({source})")
    with meta_cols[1]:
        if updated:
            st.caption(updated)

st.markdown('''
<div class="footer-note"><b>Important information</b><br>
• This assistant provides factual information about selected HDFC mutual fund schemes.<br>
• It does not offer personalised investment advice or recommend any fund.<br>
• Do not share personal or financial information.<br>
• For investment decisions, consult a qualified financial adviser.
</div>
''', unsafe_allow_html=True)
with st.expander("About this prototype"):
    st.write("This version uses deterministic matching over a small curated JSON collection. It does not connect to customer accounts or a hosted LLM.")
    st.warning("Before final submission, verify every fact, source URL and checked date against the latest official scheme documents.")
