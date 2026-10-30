from typing import List

from pydantic import BaseModel, Field


class RecommendedItem(BaseModel):
    name: str
    reason: str


class CaseStudyMatch(BaseModel):
    name: str
    reason: str
    match_type: str


class DiscoveryAnalysis(BaseModel):

    inquiry_type: str = Field(
        description="Type of enquiry"
    )

    requirement_summary: str = Field(
        description="Short summary of the client's requirement"
    )

    lead_priority: str = Field(
        description="AI-assisted priority: High, Medium, Low, or Not Applicable"
    )

    recommended_services: List[RecommendedItem]

    relevant_products: List[RecommendedItem]

    relevant_case_studies: List[CaseStudyMatch]

    discovery_questions: List[str]

    recommended_next_action: str

    draft_response: str