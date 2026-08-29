"""
Core multi-factor scoring engine for the AI Career & College Intelligence Platform.
Handles all weighted score calculations for college recommendations.
"""

from __future__ import annotations
import math
from typing import Any
import pandas as pd
from rapidfuzz import fuzz


# ─────────────────────────────────────────────
# SCORING WEIGHTS (must sum to 1.0)
# ─────────────────────────────────────────────

WEIGHTS = {
    "academic_compatibility": 0.28,
    "interest_alignment":     0.22,
    "budget_fit":             0.18,
    "location_preference":    0.12,
    "reputation_score":       0.12,
    "career_outcome":         0.08,
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Weights must sum to 1.0"


# ─────────────────────────────────────────────
# INDIVIDUAL SCORING FUNCTIONS
# ─────────────────────────────────────────────

def score_academic_compatibility(student_percentile: float, cutoff: float) -> float:
    """
    Score how well student academic performance matches college cutoff.
    Score is 100 if student is at or above cutoff.
    Drops linearly as the gap widens, but never below 0.
    """
    if cutoff <= 0:
        return 90.0

    diff = student_percentile - cutoff

    if diff >= 0:
        # At or above cutoff → high score, small bonus for over-qualification
        score = min(100.0, 85.0 + (diff * 0.5))
    else:
        # Below cutoff → penalize linearly, steep drop after -10 gap
        score = max(0.0, 80.0 + (diff * 4.0))   # loses 4pts per percentile below

    return round(score, 2)


def score_interest_alignment(student_interests: list[str], specializations_str: str) -> float:
    """
    Use RapidFuzz partial ratio matching to score alignment between
    student interests and available college specializations.
    Returns 0–100.
    """
    if not student_interests or not specializations_str:
        return 50.0

    specializations = [s.strip().lower() for s in specializations_str.split(",")]
    best_scores: list[float] = []

    for interest in student_interests:
        interest_lower = interest.lower()
        best_match = max(
            fuzz.partial_ratio(interest_lower, spec)
            for spec in specializations
        )
        best_scores.append(best_match)

    return round(sum(best_scores) / len(best_scores), 2)


def score_budget_fit(student_budget_lpa: float, college_fees_lpa: float) -> float:
    """
    Score how well the college fees fit within the student's budget.
    Perfect fit if fees ≤ budget. Penalized for exceeding budget.
    """
    if college_fees_lpa <= 0:
        return 95.0

    if student_budget_lpa <= 0:
        # No budget preference → neutral
        return 70.0

    ratio = college_fees_lpa / student_budget_lpa

    if ratio <= 0.5:
        # Significantly under budget → slightly lower (student may seek better)
        return 88.0
    elif ratio <= 0.8:
        return 95.0
    elif ratio <= 1.0:
        # Just within budget
        return 85.0
    elif ratio <= 1.2:
        return 65.0
    elif ratio <= 1.5:
        return 40.0
    else:
        return max(0.0, 40.0 - (ratio - 1.5) * 20.0)


def score_location_preference(
    college_state: str,
    college_city: str,
    preferred_states: list[str],
    preferred_cities: list[str],
) -> float:
    """
    Score location match. Returns 100 for exact city match,
    80 for state match, 60 for no preference (neutral), 30 for mismatch.
    """
    if not preferred_states and not preferred_cities:
        return 60.0  # Neutral — student has no preference

    state_lower = college_state.lower()
    city_lower = college_city.lower()

    pref_cities_lower = [c.lower() for c in preferred_cities]
    pref_states_lower = [s.lower() for s in preferred_states]

    # Fuzzy match for cities
    city_match = any(
        fuzz.partial_ratio(city_lower, pref) >= 85 for pref in pref_cities_lower
    )
    # Fuzzy match for states
    state_match = any(
        fuzz.partial_ratio(state_lower, pref) >= 85 for pref in pref_states_lower
    )

    if city_match:
        return 100.0
    elif state_match:
        return 80.0
    elif preferred_cities and not city_match:
        return 30.0
    elif preferred_states and not state_match:
        return 40.0
    return 60.0


def score_reputation(college_reputation: float) -> float:
    """Normalize reputation to 0–100 scale (already stored as 0-100)."""
    return round(min(100.0, max(0.0, float(college_reputation))), 2)


def score_career_outcome(
    placement_rate: float,
    industry_exposure: float,
    student_career_goals: list[str],
    career_outcomes_str: str,
) -> float:
    """
    Blend placement rate, industry exposure, and career goal–outcome alignment.
    """
    placement_score = float(placement_rate)
    exposure_score = float(industry_exposure)

    # Career goal alignment via fuzzy matching
    if student_career_goals and career_outcomes_str:
        outcomes = [o.strip().lower() for o in career_outcomes_str.split(",")]
        goal_scores = []
        for goal in student_career_goals:
            best = max(fuzz.partial_ratio(goal.lower(), out) for out in outcomes)
            goal_scores.append(best)
        goal_alignment = sum(goal_scores) / len(goal_scores)
    else:
        goal_alignment = 60.0

    # Weighted blend
    return round(
        placement_score * 0.4
        + exposure_score * 0.3
        + goal_alignment * 0.3,
        2,
    )


# ─────────────────────────────────────────────
# MASTER SCORING FUNCTION
# ─────────────────────────────────────────────

def compute_college_score(
    row: pd.Series,
    student_percentile: float,
    student_interests: list[str],
    student_budget_lpa: float,
    preferred_states: list[str],
    preferred_cities: list[str],
    student_career_goals: list[str],
) -> dict[str, float]:
    """
    Compute the complete multi-factor score for a single college row.
    Returns a dict with all dimension scores + overall weighted score.
    """
    academic  = score_academic_compatibility(student_percentile, float(row.get("cutoff_percentile", 80)))
    interest  = score_interest_alignment(student_interests, str(row.get("specializations", "")))
    budget    = score_budget_fit(student_budget_lpa, float(row.get("avg_fees_lpa", 0)))
    location  = score_location_preference(
                    str(row.get("state", "")),
                    str(row.get("city", "")),
                    preferred_states,
                    preferred_cities,
                )
    reputation = score_reputation(float(row.get("reputation_score", 50)))
    career     = score_career_outcome(
                    float(row.get("placement_rate", 0)),
                    float(row.get("industry_exposure", 0)),
                    student_career_goals,
                    str(row.get("career_outcomes", "")),
                )

    overall = (
        academic   * WEIGHTS["academic_compatibility"]
        + interest * WEIGHTS["interest_alignment"]
        + budget   * WEIGHTS["budget_fit"]
        + location * WEIGHTS["location_preference"]
        + reputation * WEIGHTS["reputation_score"]
        + career   * WEIGHTS["career_outcome"]
    )

    return {
        "academic_compatibility": round(academic, 2),
        "interest_alignment":     round(interest, 2),
        "budget_fit":             round(budget, 2),
        "location_preference":    round(location, 2),
        "reputation_score":       round(reputation, 2),
        "career_outcome":         round(career, 2),
        "overall":                round(overall, 2),
    }
