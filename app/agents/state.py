from typing import TypedDict, Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RequirementSpec(BaseModel):
    client_name: str = Field(default="Enterprise Client", description="Client or organization name")
    project_title: str = Field(default="Digital Transformation Proposal", description="Identified project title")
    problem_statement: str = Field(default="", description="Core problem or opportunity identified in RFP")
    key_objectives: List[str] = Field(default_factory=list, description="Primary business and technical goals")
    scope_items: List[str] = Field(default_factory=list, description="In-scope capabilities and modules")
    constraints_and_compliance: List[str] = Field(default_factory=list, description="Security, legal, and operational constraints")
    budget_or_timeline_notes: str = Field(default="", description="Any budget or timeline specifications mentioned")


class SectionOutlineItem(BaseModel):
    id: str
    title: str
    purpose: str
    key_points: List[str] = Field(default_factory=list)


class OutlineSpec(BaseModel):
    table_of_contents: List[SectionOutlineItem] = Field(default_factory=list)
    strategic_theme: str = Field(default="Enterprise Excellence")


class ExecutiveSummarySection(BaseModel):
    title: str = "1. Executive Summary"
    challenge: str = ""
    proposed_solution: str = ""
    strategic_value: str = ""
    highlights: List[str] = Field(default_factory=list)


class TechComponent(BaseModel):
    name: str
    description: str
    tech_stack: str


class TechnicalArchitectureSection(BaseModel):
    title: str = "2. Proposed Technical Architecture"
    overview: str = ""
    components: List[TechComponent] = Field(default_factory=list)
    security_and_compliance: str = ""
    scalability_and_resilience: str = ""


class PhaseDeliverable(BaseModel):
    phase: str
    duration: str
    deliverables: List[str] = Field(default_factory=list)
    outcome: str = ""


class DeliverablesSection(BaseModel):
    title: str = "3. Scope & Key Deliverables"
    phases: List[PhaseDeliverable] = Field(default_factory=list)


class PricingMilestone(BaseModel):
    milestone: str
    deliverable: str
    timeline: str
    amount: float
    percentage: str


class PricingSection(BaseModel):
    title: str = "4. Commercial & Milestone Investment"
    currency: str = "USD"
    milestones: List[PricingMilestone] = Field(default_factory=list)
    total_investment: float = 0.0
    payment_terms: str = "Net 30 days upon milestone acceptance."
    assumptions: List[str] = Field(default_factory=list)


class ReviewFeedback(BaseModel):
    compliance_score: int = Field(default=95, ge=0, le=100)
    tone_score: int = Field(default=95, ge=0, le=100)
    executive_ready: bool = True
    strengths: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    review_notes: str = ""


class ProposalSections(BaseModel):
    executive_summary: ExecutiveSummarySection = Field(default_factory=ExecutiveSummarySection)
    technical_architecture: TechnicalArchitectureSection = Field(default_factory=TechnicalArchitectureSection)
    deliverables: DeliverablesSection = Field(default_factory=DeliverablesSection)
    pricing: PricingSection = Field(default_factory=PricingSection)


class ProposalGraphState(TypedDict, total=False):
    raw_input: str
    filename: Optional[str]
    client_name: Optional[str]
    project_title: Optional[str]
    company_name: str
    currency: str
    requirements: Dict[str, Any]
    outline: Dict[str, Any]
    sections: Dict[str, Any]
    review_feedback: Dict[str, Any]
    status: str
    errors: List[str]
