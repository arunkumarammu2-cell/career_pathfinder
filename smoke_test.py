"""
Smoke test for the AI Career & College Intelligence Platform backend.
Run from the project root with: python smoke_test.py
Requires the backend to be running: uvicorn backend.app.main:app --reload
"""

import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000/api/v1"

SAMPLE_PROFILE = {
    "name": "Test Student",
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
    "interests": ["AI", "Software Engineering"],
    "budget_lpa": 5.0,
    "preferred_states": ["Maharashtra", "Karnataka"],
    "preferred_cities": ["Mumbai", "Bangalore"],
    "learning_style": "practical",
    "career_goals": ["Software Engineer", "Data Scientist"],
    "top_n": 3,
}


def get(path: str) -> dict:
    url = BASE_URL + path
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read())


def post(path: str, body: dict) -> dict:
    url = BASE_URL + path
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def check(name: str, condition: bool, detail: str = "") -> None:
    mark = "✅" if condition else "❌"
    print(f"  {mark} {name}" + (f": {detail}" if detail else ""))
    if not condition:
        sys.exit(1)


print("\n" + "="*55)
print("  AI Career Intelligence Platform — Smoke Test")
print("="*55)

# ── 1. Health check ──────────────────────────────────────────
print("\n[1] Health Check")
health = get("/health")
check("Status is 'ok'", health["status"] == "ok")
check("Dataset loaded", health["dataset_loaded"] is True)
check("Colleges in dataset", health["total_colleges"] > 0, f"{health['total_colleges']} colleges")

# ── 2. Sample profile endpoint ───────────────────────────────
print("\n[2] Sample Profile Endpoint")
sample = get("/sample-profile")
check("Has 'name' field", "name" in sample)
check("Has 'stream' field", "stream" in sample)
check("Has 'interests' list", isinstance(sample.get("interests"), list))

# ── 3. Recommendation endpoint ───────────────────────────────
print("\n[3] Recommendation Endpoint")
resp = post("/recommend", SAMPLE_PROFILE)
check("Has 'recommendations'", "recommendations" in resp)
check("Correct student name", resp["student_name"] == "Test Student")
check("Has recommendations", len(resp["recommendations"]) > 0, f"{len(resp['recommendations'])} returned")
check("Has career paths", len(resp["career_paths"]) > 0)
check("Has analytics summary", isinstance(resp.get("analytics_summary"), dict))

# Validate first recommendation structure
rec = resp["recommendations"][0]
check("Recommendation has 'rank'", "rank" in rec)
check("Recommendation has 'name'", "name" in rec and len(rec["name"]) > 0)
check("Recommendation has score_breakdown", "score_breakdown" in rec)
check("Overall score in range 0-100", 0 <= rec["score_breakdown"]["overall"] <= 100,
      f"{rec['score_breakdown']['overall']:.1f}")
check("Has 'why_this_college'", len(rec.get("why_this_college", "")) > 30)
check("Has pros list", len(rec.get("pros", [])) > 0)
check("Has cons list", len(rec.get("cons", [])) > 0)
check("Has next actions", len(rec.get("suggested_next_actions", [])) > 0)
check("Has skill improvement plan", len(rec.get("skill_improvement_plan", [])) > 0)

# ── 4. Career paths endpoint ─────────────────────────────────
print("\n[4] Career Paths Endpoint")
career_resp = post("/career-paths", SAMPLE_PROFILE)
check("Has 'career_paths'", "career_paths" in career_resp)
check("Career paths not empty", len(career_resp["career_paths"]) > 0)
cp = career_resp["career_paths"][0]
check("Career path has roadmap", len(cp.get("year_wise_roadmap", [])) > 0)
check("Career path has skills", len(cp.get("required_skills", [])) > 0)

print("\n" + "="*55)
print("  ✅ All checks passed! Backend is fully functional.")
print("="*55 + "\n")
