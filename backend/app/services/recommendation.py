"""
Recommendation Service — integrates the dataset, profiling, and scoring engine
to produce ranked college recommendations with full explanations.
"""

from __future__ import annotations

import os
import pandas as pd
from backend.app.core.scoring import compute_college_score
from backend.app.models.models import (
    CollegeRecommendation,
    ScoreBreakdown,
)
from backend.app.services.career_reasoning import (
    build_why_explanation,
    build_pros_cons,
    build_next_actions,
)
from backend.app.services.analytics import (
    compute_skill_gap,
    suggest_alternate_careers,
)


# ─────────────────────────────────────────────
# DATASET LOADING (singleton pattern)
# ─────────────────────────────────────────────

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "colleges.csv")
_DF: pd.DataFrame | None = None


def _load_dataset() -> pd.DataFrame:
    """Load and cache the colleges CSV. Returns empty DataFrame on failure."""
    global _DF
    if _DF is not None:
        return _DF

    abs_path = os.path.abspath(_DATA_PATH)
    if not os.path.exists(abs_path):
        print(f"[WARNING] Dataset not found at {abs_path}. Using empty DataFrame.")
        _DF = pd.DataFrame()
        return _DF

    df = pd.read_csv(abs_path)

    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Fill missing numeric values with safe defaults
    numeric_cols = [
        "avg_fees_lpa", "cutoff_percentile", "reputation_score",
        "placement_rate", "avg_salary_lpa", "internship_rate",
        "higher_studies_rate", "industry_exposure",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    _DF = df
    return _DF


def get_dataset_info() -> dict:
    df = _load_dataset()
    return {"loaded": not df.empty, "total_colleges": len(df)}


# ─────────────────────────────────────────────
# MAIN RECOMMENDATION FUNCTION
# ─────────────────────────────────────────────

def get_recommendations(profile: dict) -> list[CollegeRecommendation]:
    """
    Given a normalized student profile dict, score all colleges in the dataset
    and return the top-N ranked CollegeRecommendation objects.
    """
    df = _load_dataset()

    if df.empty:
        return []

    # Filter by stream match (include colleges that match or are multi-stream)
    stream = profile["stream"]
    stream_df = df[
        df["stream"].str.lower().str.contains(stream.lower(), na=False)
    ].copy()

    if stream_df.empty:
        # Fallback: return all colleges regardless of stream
        stream_df = df.copy()

    # ── Score each college ───────────────────────────────────────────────────
    scored_rows: list[dict] = []

    for _, row in stream_df.iterrows():
        score_dict = compute_college_score(
            row=row,
            student_percentile=profile["effective_percentile"],
            student_interests=profile["interests"],
            student_budget_lpa=profile["budget_lpa"],
            preferred_states=profile["preferred_states"],
            preferred_cities=profile["preferred_cities"],
            student_career_goals=profile["career_goals"],
        )
        scored_rows.append({"row": row, "scores": score_dict})

    # Sort by overall score descending
    scored_rows.sort(key=lambda x: x["scores"]["overall"], reverse=True)
    top_n = scored_rows[: profile["top_n"]]

    # ── Build Recommendation Objects ─────────────────────────────────────────
    recommendations: list[CollegeRecommendation] = []

    for rank, item in enumerate(top_n, start=1):
        row: pd.Series = item["row"]
        scores: dict = item["scores"]

        specs_str = str(row.get("specializations", ""))
        specializations = [s.strip() for s in specs_str.split(",") if s.strip()]

        score_breakdown = ScoreBreakdown(**scores)

        why = build_why_explanation(row, scores, profile)
        pros, cons = build_pros_cons(row, scores, profile)
        next_actions = build_next_actions(row, scores, profile, rank)
        skill_gaps = compute_skill_gap(profile, row)
        alternate_careers = suggest_alternate_careers(profile, scores)

        rec = CollegeRecommendation(
            rank=rank,
            college_id=str(row.get("college_id", f"C{rank:03d}")),
            name=str(row.get("name", "Unknown College")),
            state=str(row.get("state", "")),
            city=str(row.get("city", "")),
            stream=str(row.get("stream", "")),
            avg_fees_lpa=float(row.get("avg_fees_lpa", 0)),
            placement_rate=float(row.get("placement_rate", 0)),
            avg_salary_lpa=float(row.get("avg_salary_lpa", 0)),
            internship_rate=float(row.get("internship_rate", 0)),
            higher_studies_rate=float(row.get("higher_studies_rate", 0)),
            industry_exposure=float(row.get("industry_exposure", 0)),
            specializations=specializations,
            score_breakdown=score_breakdown,
            why_this_college=why,
            pros=pros,
            cons=cons,
            suggested_next_actions=next_actions,
            skill_improvement_plan=skill_gaps,
            alternate_careers=alternate_careers,
        )
        recommendations.append(rec)

    return recommendations
