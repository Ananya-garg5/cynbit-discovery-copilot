import re

ALLOWED_PRIORITY = {"High", "Medium", "Low", "Not Applicable"}
CLOSEST = "Closest example, not an exact match."
NUMBER_RE = re.compile(r"\d[\d,.]*")

BANNED_RE = re.compile(
    r"\b(?:guarantee[ds]?|certainly|best|seamless|discount)\b",
    re.IGNORECASE,
)
OVERCLAIM_RE = re.compile(
    r"\b(?:(?:has|have|had)\s+(?:\w+\s+)?experience|our\s+experience|"
    r"years\s+of\s+experience|track\s+record|proven|expertise|"
    r"we\s+(?:have|'ve)\s+(?:delivered|done|built|solved)|"
    r"specialis[ez]e?[ds]?\s+in)\b",
    re.IGNORECASE,
)
TIMELINE_PRICE_RE = re.compile(
    r"\b\d+\s*-?\s*(?:hour|day|week|month|year)s?\b"
    r"|(?:₹|rs\.?|inr|\$|usd)\s*\d",
    re.IGNORECASE,
)
INJECTION_RE = re.compile(
    r"ignore\s+(?:all\s+|any\s+)?(?:the\s+)?(?:previous|prior|above)\s+instructions"
    r"|disregard\s+(?:all\s+|the\s+)?(?:previous|prior|above)"
    r"|system\s+prompt|you\s+are\s+now"
    r"|reveal\s+your\s+(?:prompt|instructions)"
    r"|promise\s+(?:us|me)|guarantee\s+(?:us|me)",
    re.IGNORECASE,
)
FIELDS = (
    ("recommended_services", "service"),
    ("relevant_products", "product"),
    ("relevant_case_studies", "case_study"),
)


def _norm(value):
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.lower()).split())


def _numbers(text):
    return {n.rstrip(".,") for n in NUMBER_RE.findall(text)}


def apply_grounding(analysis, retrieved_documents, enquiry=""):
    """Removes ungrounded items and flags risky text. Returns (analysis, warnings)."""
    warnings = []

    if INJECTION_RE.search(enquiry):
        warnings.append(
            "The enquiry contains instruction-like or commitment-seeking text "
            "(possible prompt injection). It was ignored. Review manually."
        )

    for field, doc_type in FIELDS:
        titles = [_norm(d["title"]) for d in retrieved_documents if d["type"] == doc_type]
        kept = []
        for item in analysis.get(field, []):
            name = _norm(item["name"])
            if name and any(name in t or t in name for t in titles):
                kept.append(item)
            else:
                warnings.append(f"Removed {doc_type} not in retrieved evidence: {item['name']}")
        analysis[field] = kept

    # A short knowledge-base snippet cannot prove an exact match,
    # so every case study is presented as a closest example.
    for item in analysis["relevant_case_studies"]:
        item["match_type"] = CLOSEST

    if analysis["lead_priority"] not in ALLOWED_PRIORITY:
        warnings.append(f"Invalid lead_priority '{analysis['lead_priority']}' replaced with Medium")
        analysis["lead_priority"] = "Medium"

    draft = analysis["draft_response"]
    allowed = _numbers(enquiry) | _numbers(" ".join(d["text"] for d in retrieved_documents))
    for number in sorted(_numbers(draft) - allowed):
        warnings.append(f"Draft contains a number not found in evidence or enquiry: {number}")

    for match in sorted({m.lower() for m in BANNED_RE.findall(draft)}):
        warnings.append(f"Draft contains discouraged word: {match}")

    for match in sorted({m.group(0).lower() for m in OVERCLAIM_RE.finditer(draft)}):
        warnings.append(f"Draft may overclaim Cynbit experience ('{match}'). Reword before sending.")

    for match in sorted({m.group(0).lower() for m in TIMELINE_PRICE_RE.finditer(draft)}):
        warnings.append(f"Draft mentions a timeline or price ('{match}'). Remove it before sending.")

    return analysis, warnings