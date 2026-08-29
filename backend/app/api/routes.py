"""
API Routes for the AI Career & College Intelligence Platform.
All endpoints are defined here using absolute imports only.
"""

from __future__ import annotations
from fastapi import APIRouter, HTTPException, status
from backend.app.models.models import (
    UserProfileRequest,
    RecommendationResponse,
    HealthResponse,
)
from backend.app.services.profiling import build_profile
from backend.app.services.recommendation import get_recommendations, get_dataset_info
from backend.app.services.career_reasoning import generate_career_paths
from backend.app.services.analytics import build_analytics_summary

router = APIRouter()


# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns API health status and dataset information.",
)
def health_check() -> HealthResponse:
    info = get_dataset_info()
    return HealthResponse(
        status="ok",
        version="1.0.0",
        dataset_loaded=info["loaded"],
        total_colleges=info["total_colleges"],
    )


# ─────────────────────────────────────────────
# COLLEGE RECOMMENDATION
# ─────────────────────────────────────────────

@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get College Recommendations",
    description=(
        "Submit a student profile and receive intelligent, multi-factor college "
        "recommendations with skill gap analysis, career paths, and explanations."
    ),
)
def recommend_colleges(request: UserProfileRequest) -> RecommendationResponse:
    """
    Main recommendation endpoint.

    1. Validates user profile via Pydantic.
    2. Builds a normalized profile dict.
    3. Scores all colleges against the profile.
    4. Returns top-N recommendations with explanations.
    """
    try:
        # Step 1: Process & normalize profile
        profile = build_profile(request)

        # Step 2: Generate scored recommendations
        recommendations = get_recommendations(profile)

        if not recommendations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matching colleges found for the given profile. Try broadening your preferences.",
            )

        # Step 3: Generate career roadmaps
        career_paths = generate_career_paths(profile)

        # Step 4: Build analytics summary
        analytics = build_analytics_summary(profile, recommendations)

        return RecommendationResponse(
            student_name=profile["name"],
            stream=profile["stream"],
            total_colleges_analyzed=get_dataset_info()["total_colleges"],
            recommendations=recommendations,
            career_paths=career_paths,
            analytics_summary=analytics,
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(exc)}",
        ) from exc


# ─────────────────────────────────────────────
# CAREER PATHS ONLY
# ─────────────────────────────────────────────

@router.post(
    "/career-paths",
    summary="Get Career Paths",
    description="Returns career roadmaps for the student's stated career goals.",
)
def get_career_paths(request: UserProfileRequest) -> dict:
    profile = build_profile(request)
    paths = generate_career_paths(profile)
    return {
        "student_name": profile["name"],
        "career_goals": profile["career_goals"],
        "career_paths": [p.model_dump() for p in paths],
    }


# ─────────────────────────────────────────────
# SAMPLE PROFILE (for testing / demo)
# ─────────────────────────────────────────────

@router.get(
    "/sample-profile",
    summary="Get Sample Profile",
    description="Returns a sample UserProfileRequest body for testing in Swagger UI.",
)
def get_sample_profile() -> dict:
    return {
        "name": "Rahul Sharma",
        "stream": "Science",
        "academic_scores": {
            "maths": 92,
            "physics": 88,
            "chemistry": 85,
            "biology": 0,
            "computer_science": 95,
            "english": 80,
            "economics": 0,
            "accountancy": 0,
            "overall_percentile": 94,
        },
        "interests": ["AI", "Software Engineering", "Data Science"],
        "budget_lpa": 5.0,
        "preferred_states": ["Maharashtra", "Karnataka"],
        "preferred_cities": ["Mumbai", "Bangalore", "Pune"],
        "learning_style": "practical",
        "career_goals": ["Software Engineer", "Data Scientist"],
        "top_n": 5,
    }
