"""
Profiling Service — processes and validates raw user input into
a clean, normalized profile dictionary ready for the recommendation engine.
"""

from __future__ import annotations
from backend.app.models.models import UserProfileRequest


def build_profile(request: UserProfileRequest) -> dict:
    """
    Normalize and enrich a UserProfileRequest into a clean profile dict.

    - Computes effective percentile from raw scores if entrance percentile not provided
    - Normalizes interests and career goals to title case
    - Sets safe defaults for any missing fields
    """
    scores = request.academic_scores

    # ── Compute effective percentile ─────────────────────────────────────────
    # Use the provided overall_percentile as the primary measure.
    # If it is the default (75), try to infer from raw subject scores.
    subject_scores: list[float] = [
        v for v in [
            scores.maths,
            scores.physics,
            scores.chemistry,
            scores.biology,
            scores.computer_science,
            scores.english,
            scores.economics,
            scores.accountancy,
        ] if v > 0
    ]

    if subject_scores:
        avg_subject = sum(subject_scores) / len(subject_scores)
        # Map the 0-100 avg to a rough percentile (not linear, tapers at extremes)
        inferred_percentile = _subject_avg_to_percentile(avg_subject)
    else:
        inferred_percentile = 75.0

    # Trust the user-provided value if it deviates from the default
    effective_percentile = (
        scores.overall_percentile
        if scores.overall_percentile != 75.0
        else max(scores.overall_percentile, inferred_percentile)
    )

    # ── Normalize Text Fields ────────────────────────────────────────────────
    normalized_interests = [i.strip().title() for i in request.interests if i.strip()]
    normalized_career_goals = [g.strip().title() for g in request.career_goals if g.strip()]
    preferred_states = [s.strip().title() for s in request.preferred_states if s.strip()]
    preferred_cities = [c.strip().title() for c in request.preferred_cities if c.strip()]

    return {
        "name":                 request.name,
        "stream":               request.stream.value,
        "effective_percentile": round(effective_percentile, 2),
        "interests":            normalized_interests or ["General"],
        "budget_lpa":           request.budget_lpa,
        "preferred_states":     preferred_states,
        "preferred_cities":     preferred_cities,
        "learning_style":       request.learning_style.value,
        "career_goals":         normalized_career_goals or ["Professional"],
        "top_n":                request.top_n,
        "raw_scores": {
            "maths":            scores.maths,
            "physics":          scores.physics,
            "chemistry":        scores.chemistry,
            "biology":          scores.biology,
            "computer_science": scores.computer_science,
            "english":          scores.english,
            "economics":        scores.economics,
            "accountancy":      scores.accountancy,
        },
    }


def _subject_avg_to_percentile(avg: float) -> float:
    """
    Heuristic mapping from subject average to approximate exam percentile.
    Follows an S-curve — very high marks map to very high percentiles.
    """
    if avg >= 95:
        return 99.0
    elif avg >= 90:
        return 95.0 + (avg - 90) * 0.4
    elif avg >= 80:
        return 85.0 + (avg - 80) * 1.0
    elif avg >= 70:
        return 70.0 + (avg - 70) * 1.5
    elif avg >= 60:
        return 50.0 + (avg - 60) * 2.0
    elif avg >= 50:
        return 30.0 + (avg - 50) * 2.0
    else:
        return max(5.0, avg * 0.5)
