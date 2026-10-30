import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.classifier import classify_inquiry
from src.retriever import CynbitRetriever

B, N, A = "Business Sales Lead", "Non-Sales Enquiry", "Not Applicable"

CASES = [
    ("Hinglish clinic", "Humari clinic Jaipur mein hai, patients appointment bhool jaate hain, koi automation chahiye", B, None),
    ("Hiring + ATS build", "We are hiring and need an applicant tracking system built for our HR team.", B, None),
    ("ML training pipeline", "We need a machine learning training pipeline for our recommendation system.", B, None),
    ("Help desk AI", "Our help desk team needs an AI assistant to answer repetitive customer queries.", B, None),
    ("International SEO", "International retail chain wants better visibility on Google search for its store locations.", B, "seo"),
    ("Student internship", "I am a final-year student looking for an AI/ML internship. I have built a chatbot project.", N, None),
    ("Careers page", "Please share your careers page, I want to join your team.", N, None),
    ("Office chairs", "Please send a quote for 20 ergonomic office chairs and standing desks.", A, None),
    ("Spam", "Congratulations! You have won a prize. Click this link to claim your reward.", A, None),
    ("Cloud move", "We want to move our on-premise servers to AWS without downtime.", B, "cloud"),
    ("Old software", "Our old inventory software is slow and outdated and we want to rebuild it.", B, "legacy"),
    ("Google reviews", "Our shop gets many Google reviews and we cannot reply to all of them.", B, "revio"),
    ("Cloud internship", "Do you offer internships in cloud computing?", N, None),
    ("Greeting", "hello", A, None),
    ("Job scheduling", "We need a job scheduling system for our factory workers.", B, None),
    ("Clinic reminders", "I run a clinic in Jaipur and patients forget appointments. We need something to remind them automatically.", B, None),
    ("Invoice reminders", "We need something to remind our clients about pending invoices automatically.", B, None),
    ("Booking tool", "Our salon wants an online booking tool so customers can reserve slots.", B, None),
]

retriever = CynbitRetriever()


def route(text):
    first = classify_inquiry(text, [])
    if first == "Non-Sales Enquiry":
        return first, []
    docs = retriever.search(text, top_k=6, allowed_types=["service", "product", "case_study"])
    return classify_inquiry(text, docs), docs


class_ok = ret_ok = ret_total = 0
for name, text, expected, title_sub in CASES:
    got, docs = route(text)
    c = got == expected
    class_ok += c
    r = ""
    if title_sub:
        ret_total += 1
        hit = any(title_sub in d["title"].lower() for d in docs)
        ret_ok += hit
        r = f" | retrieval '{title_sub}': {'PASS' if hit else 'FAIL'}"
    print(f"{'PASS' if c else 'FAIL'}  {name}: expected {expected}, got {got}{r}")

print(f"\nFresh set: classification {class_ok}/{len(CASES)}, retrieval {ret_ok}/{ret_total}")