"""
Career Reasoning Service — generates human-readable explanations,
pros/cons, and next action steps for each college recommendation.
"""

from __future__ import annotations
import pandas as pd
from backend.app.models.models import CareerPath


# ─────────────────────────────────────────────
# WHY THIS COLLEGE — Natural Language
# ─────────────────────────────────────────────

def build_why_explanation(
    row: pd.Series,
    scores: dict,
    profile: dict,
) -> str:
    """
    Build a concise, human-readable explanation for why this college is recommended.
    Tailored to the student's specific profile.
    """
    name = str(row.get("name", "This college"))
    overall = scores.get("overall", 0)
    academic = scores.get("academic_compatibility", 0)
    budget = scores.get("budget_fit", 0)
    interest = scores.get("interest_alignment", 0)
    location = scores.get("location_preference", 0)

    parts: list[str] = [
        f"{name} is a {_quality_label(overall)} match for your profile ({overall:.0f}/100 overall score)."
    ]

    if academic >= 80:
        parts.append(
            f"Your academic performance aligns well with the admission requirements (score: {academic:.0f}/100)."
        )
    elif academic < 60:
        parts.append(
            f"Your academics fall slightly below the typical cutoff, so you may need to apply strategically or prepare for competitive entrance exams."
        )

    if budget >= 80:
        parts.append(
            f"The annual fee of ₹{float(row.get('avg_fees_lpa', 0)):.1f} LPA is well within your budget of ₹{profile['budget_lpa']:.1f} LPA."
        )
    elif budget < 50:
        parts.append(
            f"Note: The fees (₹{float(row.get('avg_fees_lpa', 0)):.1f} LPA) exceed your stated budget — consider scholarships or education loans."
        )

    if interest >= 70:
        parts.append(
            f"The college offers specializations that strongly align with your interests in {', '.join(profile['interests'][:3])}."
        )

    placement = float(row.get("placement_rate", 0))
    if placement >= 85:
        parts.append(
            f"With a {placement:.0f}% placement rate and an average salary of ₹{float(row.get('avg_salary_lpa', 0)):.1f} LPA, career outcomes are excellent."
        )

    if location >= 80:
        parts.append(
            f"The college is located in your preferred region ({row.get('city', '')}, {row.get('state', '')})."
        )

    return " ".join(parts)


def _quality_label(score: float) -> str:
    if score >= 85:
        return "highly excellent"
    elif score >= 70:
        return "very strong"
    elif score >= 55:
        return "good"
    elif score >= 40:
        return "moderate"
    return "low"


# ─────────────────────────────────────────────
# PROS & CONS
# ─────────────────────────────────────────────

def build_pros_cons(
    row: pd.Series,
    scores: dict,
    profile: dict,
) -> tuple[list[str], list[str]]:
    """Build a balanced list of pros and cons for the given college."""
    pros: list[str] = []
    cons: list[str] = []

    placement = float(row.get("placement_rate", 0))
    salary = float(row.get("avg_salary_lpa", 0))
    internship = float(row.get("internship_rate", 0))
    higher_studies = float(row.get("higher_studies_rate", 0))
    reputation = float(row.get("reputation_score", 0))
    fees = float(row.get("avg_fees_lpa", 0))
    budget = profile.get("budget_lpa", 5)

    # Pros
    if reputation >= 90:
        pros.append(f"🏆 Tier-1 institute with exceptional national reputation ({reputation:.0f}/100)")
    elif reputation >= 75:
        pros.append(f"⭐ Highly reputed institution recognized nationally ({reputation:.0f}/100)")

    if placement >= 85:
        pros.append(f"💼 Outstanding placement record: {placement:.0f}% of students placed")
    elif placement >= 70:
        pros.append(f"💼 Strong placement record: {placement:.0f}% placement rate")

    if salary >= 12:
        pros.append(f"💰 High average salary package: ₹{salary:.1f} LPA")
    elif salary >= 8:
        pros.append(f"💰 Competitive salary packages averaging ₹{salary:.1f} LPA")

    if internship >= 80:
        pros.append(f"🔬 Excellent internship opportunities: {internship:.0f}% internship rate")
    elif internship >= 65:
        pros.append(f"🔬 Good internship exposure: {internship:.0f}% internship rate")

    if higher_studies >= 30:
        pros.append(f"🎓 Strong higher studies pathway: {higher_studies:.0f}% pursue postgraduate education")

    if fees <= budget * 0.6:
        pros.append(f"✅ Very affordable at ₹{fees:.1f} LPA — well within your ₹{budget:.1f} LPA budget")
    elif fees <= budget:
        pros.append(f"✅ Fits within your budget at ₹{fees:.1f} LPA")

    if scores.get("interest_alignment", 0) >= 75:
        pros.append("🎯 Strong alignment between your interests and available specializations")

    # Cons
    if placement < 60:
        cons.append(f"⚠️ Below-average placement rate: {placement:.0f}% — you may need to be more self-driven in job hunting")

    if fees > budget:
        overage = fees - budget
        cons.append(f"💸 Fees exceed your budget by ₹{overage:.1f} LPA — financial planning required")

    if scores.get("academic_compatibility", 0) < 65:
        cons.append("📚 Your current academic profile is below the typical admission cutoff — preparation required")

    if scores.get("interest_alignment", 0) < 50:
        cons.append("🔀 Limited specialization match with your stated interests — explore electives carefully")

    if scores.get("location_preference", 0) < 40:
        cons.append("📍 Located outside your preferred region — consider relocation costs and lifestyle adjustments")

    if reputation < 70:
        cons.append("📊 Lower brand recognition may require more effort for top-tier placements")

    # Ensure at least one entry in each list
    if not pros:
        pros.append("✅ Provides access to quality education and professional development")
    if not cons:
        cons.append("ℹ️ No major concerns — this is a strong fit for your profile")

    return pros[:6], cons[:4]  # Cap for readability


# ─────────────────────────────────────────────
# NEXT ACTIONS
# ─────────────────────────────────────────────

def build_next_actions(
    row: pd.Series,
    scores: dict,
    profile: dict,
    rank: int,
) -> list[str]:
    """Generate personalized, actionable next steps for the student."""
    actions: list[str] = []
    name = str(row.get("name", "this college"))
    fees = float(row.get("avg_fees_lpa", 0))
    budget = profile.get("budget_lpa", 5)

    actions.append(f"📋 Visit the official website of {name} and register for admissions alerts")

    if scores.get("academic_compatibility", 0) < 70:
        actions.append(
            "📖 Focus on improving entrance exam scores — consider joining a coaching institute or online preparation platform"
        )

    if fees > budget:
        actions.append(
            "🏦 Apply for merit-based scholarships or education loans through banks (SBI Scholar Loan, Vidya Lakshmi Portal)"
        )

    if scores.get("interest_alignment", 0) >= 70:
        specializations = str(row.get("specializations", ""))
        first_spec = specializations.split(",")[0].strip() if specializations else "your chosen specialization"
        actions.append(
            f"🚀 Start building foundational projects in {first_spec} — upload to GitHub to strengthen your application portfolio"
        )

    if rank == 1:
        actions.append(
            f"⭐ This is your top match — prioritize your application here and prepare thoroughly for their specific entrance/interview process"
        )

    actions.append(
        f"🤝 Connect with {name} alumni on LinkedIn for insider tips, referrals, and placement guidance"
    )

    actions.append(
        "🎯 Prepare for common entrance exams relevant to your stream (JEE / CUET / CAT / NEET) and keep backup options ready"
    )

    return actions[:5]


# ─────────────────────────────────────────────
# CAREER PATH GENERATOR
# ─────────────────────────────────────────────

_CAREER_TEMPLATES: dict[str, dict] = {
    "software engineer": {
        "path_type": "Private",
        "avg_salary_range": "₹6–40 LPA",
        "year_wise_roadmap": [
            "Year 1: Core CS fundamentals — DSA, OOP, OS, DBMS",
            "Year 2: Web/App development projects + first internship",
            "Year 3: Specialize (Backend/Frontend/DevOps) + competitive coding",
            "Year 4: Full-time placement preparation + system design",
            "Year 5+: Tech Lead or switch to product/management track",
        ],
        "required_skills": ["Python/Java/C++", "DSA", "System Design", "Git", "Cloud (AWS/GCP)", "SQL"],
        "recommended_certifications": [
            "AWS Certified Developer", "Google Cloud Professional", "Meta Backend Developer Certificate"
        ],
    },
    "data scientist": {
        "path_type": "Private",
        "avg_salary_range": "₹8–35 LPA",
        "year_wise_roadmap": [
            "Year 1: Statistics, Python, SQL foundations",
            "Year 2: ML algorithms, data visualization, Kaggle competitions",
            "Year 3: Deep learning, NLP or Computer Vision specialization",
            "Year 4: Industry internship + research paper (optional)",
            "Year 5+: Senior DS or ML Engineer or Research Scientist",
        ],
        "required_skills": ["Python", "SQL", "Machine Learning", "Deep Learning", "Statistics", "TensorFlow/PyTorch"],
        "recommended_certifications": [
            "IBM Data Science Professional", "DeepLearning.AI Specialization", "Kaggle Competitions"
        ],
    },
    "doctor": {
        "path_type": "Government/Private",
        "avg_salary_range": "₹6–30 LPA (₹1–2Cr in private practice)",
        "year_wise_roadmap": [
            "Years 1–4.5: MBBS — Anatomy, Physiology, Pathology, Medicine",
            "Year 5: Internship (rotating) across departments",
            "Years 6–9: MD/MS specialization (optional but recommended)",
            "Year 10+: Practice, teaching, or research",
        ],
        "required_skills": ["Clinical Diagnosis", "Pharmacology", "Surgery Basics", "Patient Communication", "Research"],
        "recommended_certifications": [
            "USMLE (for US practice)", "MRCP/MRCS (UK)", "DNB Specialization"
        ],
    },
    "management consultant": {
        "path_type": "Private",
        "avg_salary_range": "₹12–60 LPA",
        "year_wise_roadmap": [
            "Year 1: MBA core — Finance, Strategy, Marketing, Operations",
            "Year 2: Specialization + summer internship at consulting firm",
            "Year 3: Join as Associate/Analyst at Big 4 or MBB",
            "Year 5+: Manager/Senior Manager track",
            "Year 10+: Partner or transition to industry leadership",
        ],
        "required_skills": ["Problem Solving", "Data Analysis", "Excel/PowerBI", "Communication", "Project Management"],
        "recommended_certifications": [
            "CFA Level 1", "PMP Certification", "Six Sigma Green Belt"
        ],
    },
    "civil services": {
        "path_type": "Government",
        "avg_salary_range": "₹9–25 LPA (Grade Pay + Allowances)",
        "year_wise_roadmap": [
            "Graduation: Choose a strong optional subject + follow NCERT",
            "Year 1 (Prep): Current affairs + GS Paper thorough study",
            "Year 2 (Prelims): Mock tests + previous year papers",
            "Year 3 (Mains): Essay + optional subject mastery",
            "Interview: Personality test preparation + current affairs",
        ],
        "required_skills": ["Current Affairs", "Essay Writing", "GS Paper 1–4", "Optional Subject Mastery", "Ethics"],
        "recommended_certifications": [
            "Forum IAS / Vajiram classroom", "UPSC Prelims Test Series", "Vision IAS GS Foundation"
        ],
    },
    "designer": {
        "path_type": "Private/Startup",
        "avg_salary_range": "₹4–25 LPA",
        "year_wise_roadmap": [
            "Year 1: Design fundamentals — color, typography, composition",
            "Year 2: UI/UX tools (Figma, Adobe XD) + portfolio projects",
            "Year 3: Specialize (Product Design, Motion, Brand Identity)",
            "Year 4: Internships + real client projects",
            "Year 5+: Senior Designer or Creative Director",
        ],
        "required_skills": ["Figma", "Adobe Suite", "Design Thinking", "User Research", "Prototyping"],
        "recommended_certifications": [
            "Google UX Design Certificate", "Interaction Design Foundation", "Adobe Certified Professional"
        ],
    },
}

_DEFAULT_CAREER = {
    "path_type": "Private",
    "avg_salary_range": "₹5–20 LPA",
    "year_wise_roadmap": [
        "Year 1: Build foundational knowledge in your chosen field",
        "Year 2: Gain practical experience through internships",
        "Year 3–4: Specialize and build a professional portfolio",
        "Year 5+: Grow into senior roles or entrepreneurship",
    ],
    "required_skills": ["Domain Knowledge", "Communication", "Problem Solving", "Teamwork"],
    "recommended_certifications": ["Domain-specific online certifications (Coursera, Udemy, edX)"],
}


def generate_career_paths(profile: dict) -> list[CareerPath]:
    """Generate relevant career path roadmaps based on career goals."""
    paths: list[CareerPath] = []
    seen: set[str] = set()

    for goal in profile.get("career_goals", [])[:3]:
        goal_key = _best_career_key(goal)
        if goal_key in seen:
            continue
        seen.add(goal_key)

        template = _CAREER_TEMPLATES.get(goal_key, _DEFAULT_CAREER)

        paths.append(CareerPath(
            career_title=goal.title(),
            path_type=template["path_type"],
            avg_salary_range=template["avg_salary_range"],
            year_wise_roadmap=template["year_wise_roadmap"],
            required_skills=template["required_skills"],
            recommended_certifications=template["recommended_certifications"],
        ))

    if not paths:
        paths.append(CareerPath(
            career_title="Professional Career",
            **_DEFAULT_CAREER,
        ))

    return paths


def _best_career_key(goal: str) -> str:
    goal_lower = goal.lower()
    for key in _CAREER_TEMPLATES:
        if key in goal_lower or goal_lower in key:
            return key
    # Fuzzy keyword matching
    mapping = {
        "software": "software engineer",
        "developer": "software engineer",
        "coder": "software engineer",
        "data": "data scientist",
        "ml": "data scientist",
        "ai": "data scientist",
        "doctor": "doctor",
        "medical": "doctor",
        "mbbs": "doctor",
        "mba": "management consultant",
        "manager": "management consultant",
        "consultant": "management consultant",
        "ias": "civil services",
        "ips": "civil services",
        "upsc": "civil services",
        "government": "civil services",
        "design": "designer",
        "ux": "designer",
        "ui": "designer",
    }
    for keyword, career_key in mapping.items():
        if keyword in goal_lower:
            return career_key
    return "software engineer"  # safe default
