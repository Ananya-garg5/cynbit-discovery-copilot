import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.analyzer import CynbitAnalyzer  # noqa: E402
from src.classifier import classify_inquiry  # noqa: E402
from src.retriever import CynbitRetriever  # noqa: E402

SAMPLES_PATH = ROOT / "evaluation" / "sample_outputs.json"
ALLOWED_TYPES = ["service", "product", "case_study"]

EXAMPLES = {
    "Clinic reminders": "I run a clinic in Jaipur and patients forget appointments. We need something to remind them automatically.",
    "Cloud migration": "We want to move our on-premise servers to AWS without downtime.",
    "Google reviews": "Our shop gets many Google reviews and we cannot reply to all of them.",
    "Internship": "I am a final-year student looking for an AI/ML internship.",
    "Office chairs": "Please send a quote for 20 ergonomic office chairs and standing desks.",
}

st.set_page_config(page_title="Cynbit Discovery Copilot", layout="wide")


@st.cache_resource
def get_retriever():
    return CynbitRetriever()


@st.cache_resource
def get_analyzer():
    return CynbitAnalyzer()


def load_samples():
    if SAMPLES_PATH.exists():
        try:
            return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))
        except ValueError:
            return []
    return []


def is_quota_error(error_text):
    text = error_text.lower()
    return any(key in text for key in ("429", "resource_exhausted", "quota", "rate limit"))


def preview(enquiry):
    """Deterministic classification + retrieval. Needs no API key."""
    retriever = get_retriever()
    first = classify_inquiry(enquiry, [])
    if first == "Non-Sales Enquiry":
        return first, []
    docs = retriever.search(enquiry, top_k=6, allowed_types=ALLOWED_TYPES)
    return classify_inquiry(enquiry, docs), docs


def run_analysis(enquiry):
    try:
        result = get_analyzer().analyze(enquiry)
        return {"kind": "full", "result": result, "enquiry": enquiry, "saved": False}
    except Exception as error:  # noqa: BLE001
        label, docs = preview(enquiry)
        return {
            "kind": "preview",
            "classification": label,
            "docs": docs,
            "error": f"{type(error).__name__}: {error}",
            "enquiry": enquiry,
        }


def set_example(text):
    st.session_state["enquiry_text"] = text


def show_documents(docs):
    if not docs:
        st.write("No Cynbit knowledge retrieved.")
        return
    for doc in docs:
        st.markdown(f"**{doc['title']}**  ·  {doc['type']}  ·  score {doc['score']}")
        st.caption(doc["source_url"])
        st.write(doc["text"])
        st.divider()


def show_items(items, with_match_type=False):
    if not items:
        st.write("None supported by the retrieved evidence.")
        return
    for item in items:
        st.markdown(f"**{item['name']}**")
        if with_match_type:
            st.caption(item["match_type"])
        st.write(item["reason"])


def show_full(view):
    result = view["result"]
    analysis = result["analysis"]
    docs = result["retrieved_documents"]
    inquiry_type = analysis["inquiry_type"]

    if view.get("saved"):
        st.info("Showing a saved result generated earlier. No API call was made.")

    left, right = st.columns(2)
    left.metric("Classification", inquiry_type)
    right.metric("Lead priority (AI-assisted heuristic)", analysis["lead_priority"])

    st.subheader("Requirement summary")
    st.write(analysis["requirement_summary"])

    if inquiry_type == "Business Sales Lead":
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("Recommended services")
            show_items(analysis["recommended_services"])
        with c2:
            st.subheader("Relevant products")
            show_items(analysis["relevant_products"])
        with c3:
            st.subheader("Case studies")
            show_items(analysis["relevant_case_studies"], with_match_type=True)

        st.subheader("Discovery questions")
        for question in analysis["discovery_questions"]:
            st.markdown(f"- {question}")

    st.subheader("Recommended next action")
    st.write(analysis["recommended_next_action"])

    for warning in analysis.get("warnings", []):
        st.warning(warning)

    st.subheader("Draft response (edit before sending)")
    st.text_area(
        "Draft",
        value=analysis["draft_response"],
        height=240,
        key=f"draft_{hash(view['enquiry'])}_{view.get('saved', False)}",
        label_visibility="collapsed",
    )
    st.caption(
        "AI-assisted draft. A human must review it before anything is sent. "
        "Lead priority is a heuristic, not an official Cynbit qualification rule."
    )

    with st.expander("Retrieved Cynbit evidence"):
        show_documents(docs)


def show_preview(view):
    error_text = view["error"]

    if "GEMINI_API_KEY is missing" in error_text:
        st.warning("No Gemini API key found. Showing classification and retrieved evidence only.")
    elif is_quota_error(error_text):
        st.warning(
            "The Gemini request quota is exhausted. Classification and retrieval still "
            "worked; only the generated analysis is unavailable. Try again later or open "
            "a saved example from the sidebar."
        )
    else:
        st.error("The generation step failed. Classification and retrieval still worked.")

    with st.expander("Technical details"):
        st.code(error_text)

    st.metric("Classification", view["classification"])
    with st.expander("Retrieved Cynbit evidence", expanded=True):
        show_documents(view["docs"])


# ---------------------------------------------------------------- page

st.title("Cynbit Discovery Copilot")
st.caption(
    "Prepares a discovery brief from a prospective enquiry using Cynbit's public website "
    "knowledge. A human reviews everything before anything is sent."
)

samples = load_samples()
with st.sidebar:
    st.header("Saved examples")
    if samples:
        index = st.selectbox(
            "Pick a saved result (no API call)",
            range(len(samples)),
            format_func=lambda i: samples[i]["enquiry"][:70],
        )
        if st.button("Show saved result"):
            sample = samples[index]
            st.session_state["view"] = {
                "kind": "full",
                "saved": True,
                "enquiry": sample["enquiry"],
                "result": {
                    "analysis": sample["analysis"],
                    "retrieved_documents": sample["retrieved_documents"],
                },
            }
    else:
        st.write("None yet. Run scripts/generate_samples.py to create them.")

st.write("Try an example:")
columns = st.columns(len(EXAMPLES))
for column, (label, text) in zip(columns, EXAMPLES.items()):
    column.button(label, on_click=set_example, args=(text,), use_container_width=True)

enquiry = st.text_area(
    "Client enquiry",
    key="enquiry_text",
    height=150,
    placeholder="Paste or type the prospective client's message here.",
)

if st.button("Analyze enquiry", type="primary"):
    if not enquiry.strip():
        st.warning("Please enter an enquiry first.")
    else:
        with st.spinner("Analyzing..."):
            st.session_state["view"] = run_analysis(enquiry.strip())

view = st.session_state.get("view")
if view:
    st.divider()
    if view["kind"] == "full":
        show_full(view)
    else:
        show_preview(view)