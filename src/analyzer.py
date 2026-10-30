import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.classifier import classify_inquiry
from src.grounding import apply_grounding
from src.prompts import SYSTEM_PROMPT, build_analysis_prompt
from src.retriever import CynbitRetriever
from src.schemas import DiscoveryAnalysis

load_dotenv()

DEFAULT_MODEL = "gemini-3-flash-preview"


def _static_result(inquiry_type, summary, next_action, draft, documents):
    return {
        "analysis": {
            "inquiry_type": inquiry_type,
            "requirement_summary": summary,
            "lead_priority": "Not Applicable",
            "recommended_services": [],
            "relevant_products": [],
            "relevant_case_studies": [],
            "discovery_questions": [],
            "recommended_next_action": next_action,
            "draft_response": draft,
            "warnings": [],
        },
        "retrieved_documents": documents,
    }


def _strip_fences(text):
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip())


class CynbitAnalyzer:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing. Add it to your .env file.")

        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
        self.retriever = CynbitRetriever()

    def _generate(self, prompt):
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=DiscoveryAnalysis,
            temperature=0.2,
        )
        last_error = None
        for _ in range(2):  # retry only on invalid JSON, never on API errors
            response = self.client.models.generate_content(
                model=self.model, contents=prompt, config=config
            )
            try:
                return DiscoveryAnalysis.model_validate_json(_strip_fences(response.text))
            except ValueError as error:
                last_error = error
        raise ValueError(f"Gemini returned invalid JSON twice: {last_error}")

    def analyze(self, enquiry: str, top_k: int = 6):
        inquiry_type = classify_inquiry(enquiry, retrieved_documents=[])

        if inquiry_type == "Non-Sales Enquiry":
            return _static_result(
                inquiry_type,
                "This enquiry is about a career, internship, training or employment "
                "request rather than a client business requirement.",
                "Route the enquiry to the appropriate careers or recruitment process.",
                "Thank you for your interest in Cynbit. This enquiry appears to be about "
                "careers or internship opportunities rather than a business project. "
                "Please refer to Cynbit's careers information for relevant opportunities.",
                [],
            )

        retrieved_documents = self.retriever.search(
            enquiry, top_k=top_k, allowed_types=["service", "product", "case_study"]
        )
        inquiry_type = classify_inquiry(enquiry, retrieved_documents)

        if inquiry_type == "Not Applicable":
            return _static_result(
                inquiry_type,
                "The enquiry does not appear to match Cynbit's publicly available "
                "services, products or case studies.",
                "No business sales action is recommended unless more context "
                "establishes a relevant requirement.",
                "Thank you for reaching out. We would need more information about your "
                "technology or business requirement to determine whether Cynbit's "
                "capabilities are relevant.",
                retrieved_documents,
            )

        prompt = build_analysis_prompt(enquiry, retrieved_documents, inquiry_type)
        analysis = self._generate(prompt).model_dump()
        analysis["inquiry_type"] = inquiry_type  # classifier stays the authority

        analysis, warnings = apply_grounding(analysis, retrieved_documents, enquiry)
        analysis["warnings"] = warnings

        return {"analysis": analysis, "retrieved_documents": retrieved_documents}