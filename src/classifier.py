import re

MIN_EVIDENCE_SCORE = 0.12  # used only when the enquiry has no business keyword


def _pattern(words):
    body = "|".join(re.escape(word) for word in words)
    return re.compile(rf"\b(?:{body})(?:s|es)?\b")


# Always a career/internship enquiry.
STRONG_CAREER = _pattern([
    "internship", "intern", "resume", "cv", "fresher", "vacancy",
    "vacancies", "career", "recruitment", "work with cynbit", "job opening",
])

# Ambiguous words: career enquiry unless a company is clearly asking for a build.
WEAK_CAREER = _pattern(["job", "hiring", "employment", "placement", "training"])

COMPANY_SIGNALS = _pattern(["we", "our", "my company", "my business", "our company"])

HELPDESK = re.compile(r"\b(?:help|service|support|front)\s+desk\b")

OUT_OF_SCOPE = _pattern([
    "office furniture", "furniture", "chair", "desk", "office supplies",
    "stationery", "printer", "carpet", "office equipment",
    "furniture catalogue", "furniture catalog",
])

BUSINESS = _pattern([
    "business", "client", "project", "requirement", "workflow", "automation",
    "automate", "automated", "software", "platform", "system", "website",
    "application", "app", "api", "server", "development", "integration",
    "migration", "cloud", "ai", "artificial intelligence", "machine learning",
    "llm", "chatbot", "agent", "crm", "seo", "data", "document", "process",
    "analytics", "infrastructure", "review", "customer reviews", "feedback",
    "rating",
    "automatically", "automatic", "remind", "reminding", "reminder",
    "appointment", "booking", "patient", "invoice", "inventory",
    "dashboard", "tracking", "technology", "digital", "tool",
])

RELEVANT_TYPES = {"service", "product", "case_study"}


def classify_inquiry(enquiry: str, retrieved_documents=None) -> str:
    """Returns: Non-Sales Enquiry, Business Sales Lead, or Not Applicable."""
    text = enquiry.lower().strip()

    if STRONG_CAREER.search(text):
        return "Non-Sales Enquiry"

    if OUT_OF_SCOPE.search(HELPDESK.sub(" ", text)):
        return "Not Applicable"

    has_business = bool(BUSINESS.search(text))

    if WEAK_CAREER.search(text) and not (COMPANY_SIGNALS.search(text) and has_business):
        return "Non-Sales Enquiry"

    if has_business:
        return "Business Sales Lead"

    # No business keyword: accept only if the retrieved evidence is strong.
    if retrieved_documents:
        best = max(
            (d.get("score", 0) for d in retrieved_documents if d.get("type") in RELEVANT_TYPES),
            default=0,
        )
        if best >= MIN_EVIDENCE_SCORE:
            return "Business Sales Lead"

    return "Not Applicable"