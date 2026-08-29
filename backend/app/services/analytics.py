"""
Analytics Service — performs skill gap analysis, placement likelihood estimation,
and alternate career suggestion based on the student profile and college data.
"""

from __future__ import annotations
import pandas as pd
from backend.app.models.models import SkillGap


# ─────────────────────────────────────────────
# SKILL LIBRARY — Interest → Required Skills
# ─────────────────────────────────────────────

_SKILL_MAP: dict[str, list[tuple[str, str, list[str]]]] = {
    # (skill_name, importance, [resources])
    "software engineering": [
        ("Data Structures & Algorithms", "Critical", ["LeetCode", "GeeksForGeeks", "CLRS Book"]),
        ("System Design", "Critical", ["Grokking System Design", "ByteByteGo"]),
        ("Python or Java", "Critical", ["Python.org", "CS50 Harvard"]),
        ("SQL & Databases", "Important", ["SQLZoo", "PostgreSQL Tutorial"]),
        ("Git & Version Control", "Important", ["Pro Git Book", "GitHub Learning Lab"]),
        ("Cloud Basics (AWS/GCP)", "Nice to have", ["AWS Skill Builder", "Google Cloud Training"]),
    ],
    "ai": [
        ("Python Programming", "Critical", ["Python.org", "Automate the Boring Stuff"]),
        ("Machine Learning", "Critical", ["Andrew Ng ML Course (Coursera)", "Fast.ai"]),
        ("Linear Algebra & Statistics", "Critical", ["Khan Academy", "3Blue1Brown"]),
        ("Deep Learning (TensorFlow/PyTorch)", "Important", ["DeepLearning.AI Specialization"]),
        ("Data Wrangling (Pandas)", "Important", ["Kaggle Courses", "Real Python"]),
        ("Research Paper Reading", "Nice to have", ["arXiv.org", "Papers With Code"]),
    ],
    "data science": [
        ("Statistics & Probability", "Critical", ["StatQuest YouTube", "Khan Academy"]),
        ("Python + Pandas", "Critical", ["Kaggle Python Course", "DataCamp"]),
        ("Machine Learning", "Critical", ["Scikit-learn Docs", "Coursera ML Specialization"]),
        ("SQL", "Important", ["Mode SQL Tutorial", "SQLZoo"]),
        ("Data Visualization", "Important", ["Matplotlib", "Tableau Public", "Seaborn"]),
        ("Storytelling with Data", "Nice to have", ["book: Storytelling with Data by Cole N."]),
    ],
    "medicine": [
        ("Biology & Biochemistry", "Critical", ["NCERT Biology", "Campbell Biology"]),
        ("Physiology", "Critical", ["Guyton & Hall Textbook"]),
        ("Clinical Diagnosis Thinking", "Critical", ["Case-based Learning", "Clinical Medicine Oxford"]),
        ("Research Methodology", "Important", ["Cochrane EPOC", "PubMed basics"]),
        ("Communication & Empathy", "Important", ["Medical Ethics courses (Coursera)"]),
    ],
    "business": [
        ("Financial Accounting", "Critical", ["NCERT Accountancy", "Investopedia"]),
        ("Business Strategy", "Critical", ["Business Model Generation book", "HBS Case Studies"]),
        ("Excel & Data Analysis", "Important", ["Excel Jet", "CFI Excel Course"]),
        ("Communication & Presentation", "Important", ["Toastmasters", "Presentation Zen book"]),
        ("Marketing Fundamentals", "Nice to have", ["Philip Kotler Marketing", "HubSpot Academy"]),
    ],
    "design": [
        ("Design Fundamentals", "Critical", ["Canva Design School", "IDEO Design Thinking"]),
        ("Figma / Adobe XD", "Critical", ["Figma Academy", "YouTube Tutorials"]),
        ("User Research", "Important", ["Interaction Design Foundation", "Nielsen Norman Group"]),
        ("Typography & Color Theory", "Important", ["Practical Typography book", "Coolors.co"]),
        ("Portfolio Building", "Nice to have", ["Behance", "Dribbble"]),
    ],
    "government": [
        ("Current Affairs & GK", "Critical", ["The Hindu newspaper", "Vision IAS Monthly"]),
        ("Essay Writing", "Critical", ["Vajiram Essay Module", "Insights on India"]),
        ("GS Paper 1–4", "Critical", ["Mrunal YouTube", "Forum IAS Notes"]),
        ("Optional Subject Mastery", "Important", ["IGNOU Study Material", "Unacademy"]),
        ("Interview Preparation", "Nice to have", ["Mock Interviews", "UPSC Previous Papers"]),
    ],
}

_DEFAULT_SKILLS = [
    ("Communication Skills", "Critical", ["Speak with confidence courses (Coursera)"]),
    ("Problem Solving", "Critical", ["Brilliant.org", "Project Euler"]),
    ("Domain Knowledge", "Important", ["YouTube, MOOCs relevant to your field"]),
    ("Time Management", "Nice to have", ["Getting Things Done book", "Todoist"]),
]


def compute_skill_gap(profile: dict, college_row: pd.Series) -> list[SkillGap]:
    """
    Determine skill gaps based on student interests and career goals.
    Returns a list of SkillGap objects prioritized by importance.
    """
    combined_keywords = " ".join(
        profile.get("interests", []) + profile.get("career_goals", [])
    ).lower()

    skill_list: list[tuple[str, str, list[str]]] = []
    seen_keys: set[str] = set()

    for key, skills in _SKILL_MAP.items():
        if key in combined_keywords or any(word in combined_keywords for word in key.split()):
            for skill_tuple in skills:
                if skill_tuple[0] not in seen_keys:
                    seen_keys.add(skill_tuple[0])
                    skill_list.append(skill_tuple)

    if not skill_list:
        skill_list = _DEFAULT_SKILLS.copy()

    # Sort by importance (Critical first)
    importance_order = {"Critical": 0, "Important": 1, "Nice to have": 2}
    skill_list.sort(key=lambda x: importance_order.get(x[1], 99))

    return [
        SkillGap(skill=name, importance=importance, resources=resources)
        for name, importance, resources in skill_list[:6]  # top 6
    ]


# ─────────────────────────────────────────────
# ALTERNATE CAREER SUGGESTIONS
# ─────────────────────────────────────────────

_ALTERNATE_CAREER_MAP: dict[str, list[str]] = {
    "very low academic": [
        "Polytechnic Diploma programs (Mechanical, Civil, Electronics)",
        "ITI (Industrial Training Institute) certifications",
        "Skill India trades (Electrician, Plumber, HVAC Technician)",
        "Government exam preparation (SSC, RRB, Banking)",
    ],
    "low academic": [
        "BCA (Bachelor of Computer Applications) + MCA pathway",
        "BSc in relevant subjects + B.Ed for teaching",
        "Diploma in Design, Animation, or Mass Communication",
        "Government sector jobs (clerical level — SSC CHSL)",
    ],
    "medium academic": [
        "PGDM from a decent B-School",
        "State-level engineering colleges",
        "Chartered Accountancy (CA) pathway",
        "NIFT / NID for design-oriented students",
    ],
    "high academic": [
        "IITs, NITs, IIMs — prepare hard!",
        "BITS Pilani / IIIT Hyderabad",
        "AIIMS / AFMC for medical aspirants",
        "Research fellowships (CSIR, BARC, DRDO)",
    ],
}

_INTEREST_ALTERNATES: dict[str, list[str]] = {
    "ai": ["ML Engineer", "Data Analyst", "Research Scientist", "AI Product Manager"],
    "medicine": ["Pharmacy (B.Pharm)", "Physiotherapy", "Medical Research", "Hospital Administration"],
    "business": ["Stock Market Analysis", "Entrepreneurship", "Supply Chain Management", "E-commerce"],
    "design": ["UI/UX Designer", "Graphic Designer", "Game Designer", "Motion Graphics Artist"],
    "government": ["Banking (IBPS/SBI)", "Railway Exams (RRB)", "Defence (NDA/CDS)", "State PSC"],
    "software engineering": ["QA Testing", "DevOps Engineer", "IT Support", "Cybersecurity Analyst"],
}


def suggest_alternate_careers(profile: dict, scores: dict) -> list[str]:
    """
    Suggest alternate career paths based on academic performance level
    and primary interests, particularly useful when main scores are lower.
    """
    overall = scores.get("overall", 50)
    academic = scores.get("academic_compatibility", 50)
    alternates: list[str] = []

    # Academic-level based fallback suggestions
    if academic < 50:
        alternates.extend(_ALTERNATE_CAREER_MAP["very low academic"][:2])
    elif academic < 65:
        alternates.extend(_ALTERNATE_CAREER_MAP["low academic"][:2])
    elif academic < 80:
        alternates.extend(_ALTERNATE_CAREER_MAP["medium academic"][:2])
    else:
        alternates.extend(_ALTERNATE_CAREER_MAP["high academic"][:2])

    # Interest-based alternates
    combined = " ".join(profile.get("interests", []) + profile.get("career_goals", [])).lower()
    for key, careers in _INTEREST_ALTERNATES.items():
        if key in combined:
            alternates.extend(careers[:2])
            break

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for item in alternates:
        if item not in seen:
            seen.add(item)
            unique.append(item)

    return unique[:5]


# ─────────────────────────────────────────────
# ANALYTICS SUMMARY (for response snapshot)
# ─────────────────────────────────────────────

def build_analytics_summary(profile: dict, recommendations: list) -> dict:
    """Build a quick analytics snapshot for the response."""
    if not recommendations:
        return {"message": "No recommendations generated."}

    avg_placement = sum(r.placement_rate for r in recommendations) / len(recommendations)
    avg_fees = sum(r.avg_fees_lpa for r in recommendations) / len(recommendations)
    avg_salary = sum(r.avg_salary_lpa for r in recommendations) / len(recommendations)
    top_score = recommendations[0].score_breakdown.overall

    return {
        "top_match_score": round(top_score, 1),
        "avg_placement_rate": round(avg_placement, 1),
        "avg_fees_lpa": round(avg_fees, 2),
        "avg_salary_lpa": round(avg_salary, 2),
        "colleges_analyzed": len(recommendations),
        "budget_status": (
            "✅ All recommendations fit your budget"
            if all(r.avg_fees_lpa <= profile["budget_lpa"] for r in recommendations)
            else "⚠️ Some recommendations exceed your stated budget"
        ),
        "internship_probability": f"{sum(r.internship_rate for r in recommendations) / len(recommendations):.1f}%",
        "higher_studies_likelihood": f"{sum(r.higher_studies_rate for r in recommendations) / len(recommendations):.1f}%",
    }
