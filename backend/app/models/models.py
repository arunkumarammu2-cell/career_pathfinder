"""
Pydantic v2 Models for the AI Career & College Intelligence Platform.
All request and response schemas are defined here.
"""

from __future__ import annotations
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from enum import Enum


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class Stream(str, Enum):
    science = "Science"
    commerce = "Commerce"
    arts = "Arts"


class LearningStyle(str, Enum):
    theory = "theory"
    practical = "practical"
    mixed = "mixed"


class BudgetRange(str, Enum):
    very_low = "0-1"        # 0 to 1 LPA
    low = "1-3"             # 1 to 3 LPA
    medium = "3-6"          # 3 to 6 LPA
    high = "6-12"           # 6 to 12 LPA
    very_high = "12+"       # 12+ LPA


# ─────────────────────────────────────────────
# REQUEST MODELS
# ─────────────────────────────────────────────

class AcademicScores(BaseModel):
    maths: Annotated[float, Field(ge=0, le=100, description="Maths score (0-100)")] = 0.0
    physics: Annotated[float, Field(ge=0, le=100, description="Physics score (0-100)")] = 0.0
    chemistry: Annotated[float, Field(ge=0, le=100, description="Chemistry score (0-100)")] = 0.0
    biology: Annotated[float, Field(ge=0, le=100, description="Biology score (0-100)")] = 0.0
    computer_science: Annotated[float, Field(ge=0, le=100, description="CS score (0-100)")] = 0.0
    english: Annotated[float, Field(ge=0, le=100, description="English score (0-100)")] = 70.0
    economics: Annotated[float, Field(ge=0, le=100, description="Economics score (0-100)")] = 0.0
    accountancy: Annotated[float, Field(ge=0, le=100, description="Accountancy score (0-100)")] = 0.0
    overall_percentile: Annotated[float, Field(ge=0, le=100, description="Entrance exam percentile")] = 75.0


class UserProfileRequest(BaseModel):
    name: str = Field(default="Student", min_length=1, max_length=100)
    stream: Stream = Stream.science
    academic_scores: AcademicScores = Field(default_factory=AcademicScores)
    interests: list[str] = Field(
        default=["Software Engineering"],
        description="List of interest areas e.g. AI, Medicine, Business, Design"
    )
    budget_lpa: Annotated[float, Field(ge=0, le=50, description="Max annual budget in LPA")] = 5.0
    preferred_states: list[str] = Field(default=[], description="Preferred states (empty = no preference)")
    preferred_cities: list[str] = Field(default=[], description="Preferred cities (empty = no preference)")
    learning_style: LearningStyle = LearningStyle.mixed
    career_goals: list[str] = Field(
        default=["Software Engineer"],
        description="Target career paths"
    )
    top_n: Annotated[int, Field(ge=1, le=20, description="Number of recommendations to return")] = 5


# ─────────────────────────────────────────────
# RESPONSE MODELS
# ─────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    academic_compatibility: float = Field(description="How well academic profile fits college cutoff (0-100)")
    interest_alignment: float = Field(description="How well interests match available specializations (0-100)")
    budget_fit: float = Field(description="How well budget matches college fees (0-100)")
    location_preference: float = Field(description="Location preference match score (0-100)")
    reputation_score: float = Field(description="College reputation score (0-100)")
    career_outcome: float = Field(description="Career outcome probability (0-100)")
    overall: float = Field(description="Weighted overall match score (0-100)")


class SkillGap(BaseModel):
    skill: str
    importance: str   # Critical / Important / Nice to have
    resources: list[str]


class CareerPath(BaseModel):
    career_title: str
    path_type: str   # Government / Private / Startup / Research
    avg_salary_range: str
    year_wise_roadmap: list[str]
    required_skills: list[str]
    recommended_certifications: list[str]


class CollegeRecommendation(BaseModel):
    rank: int
    college_id: str
    name: str
    state: str
    city: str
    stream: str
    avg_fees_lpa: float
    placement_rate: float
    avg_salary_lpa: float
    internship_rate: float
    higher_studies_rate: float
    industry_exposure: float
    specializations: list[str]
    score_breakdown: ScoreBreakdown
    why_this_college: str
    pros: list[str]
    cons: list[str]
    suggested_next_actions: list[str]
    skill_improvement_plan: list[SkillGap]
    alternate_careers: list[str]


class RecommendationResponse(BaseModel):
    student_name: str
    stream: str
    total_colleges_analyzed: int
    recommendations: list[CollegeRecommendation]
    career_paths: list[CareerPath]
    analytics_summary: dict  # quick stats snapshot


class HealthResponse(BaseModel):
    status: str
    version: str
    dataset_loaded: bool
    total_colleges: int
