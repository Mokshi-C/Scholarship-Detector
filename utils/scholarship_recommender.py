"""
Scholarship Recommendation Engine.
Matches a student's profile against a set of real scholarship schemes
and returns ranked recommendations with match scores and reasons.
"""

SCHOLARSHIP_SCHEMES = [
    {
        "name": "Central Sector Scholarship",
        "provider": "Ministry of Education, Govt. of India",
        "rules": {
            "min_marks": 80,
            "max_income": 800000,
            "degree_levels": ["undergraduate", "ug", "b.tech", "b.e.", "b.sc",
                               "b.com", "ba", "bba", "bca"]
        }
    },
    {
        "name": "Post Matric Scholarship (SC)",
        "provider": "Ministry of Social Justice & Empowerment",
        "rules": {
            "category": ["SC"],
            "max_income": 250000
        }
    },
    {
        "name": "Post Matric Scholarship (ST)",
        "provider": "Ministry of Tribal Affairs",
        "rules": {
            "category": ["ST"],
            "max_income": 250000
        }
    },
    {
        "name": "Merit-cum-Means Scholarship",
        "provider": "Ministry of Minority Affairs",
        "rules": {
            "min_marks": 60,
            "max_income": 250000,
            "minority_categories": ["Muslim", "Christian", "Sikh", "Buddhist",
                                     "Parsi", "Jain", "Minority"]
        }
    },
    {
        "name": "AICTE Pragati Scholarship",
        "provider": "AICTE",
        "rules": {
            "gender": "Female",
            "technical_courses": ["b.tech", "b.e.", "diploma", "polytechnic",
                                   "m.tech", "mca", "bca"],
            "max_income": 800000
        }
    },
]


def _is_technical_course(course: str) -> bool:
    course_l = (course or "").lower()
    return any(t in course_l for t in
               ["b.tech", "b.e.", "diploma", "polytechnic", "m.tech", "mca", "bca"])


def _is_undergraduate(course: str) -> bool:
    course_l = (course or "").lower()
    return any(t in course_l for t in
               ["b.tech", "b.e.", "b.sc", "b.com", "ba", "bba", "bca", "undergraduate"])


def _is_minority(category: str) -> bool:
    return (category or "").strip().lower() in [
        c.lower() for c in ["Muslim", "Christian", "Sikh", "Buddhist",
                             "Parsi", "Jain", "Minority"]
    ]


def _score_scholarship(scheme: dict, student: dict) -> dict:
    """
    Compute a match score (0-100), eligibility flag, and a human-readable
    reason for a single scholarship scheme.
    """
    name = scheme["name"]
    rules = scheme["rules"]

    income = float(student.get("income", 0))
    marks = float(student.get("marks", 0))
    category = (student.get("category", "") or "").strip()
    course = student.get("course", "") or ""
    gender = (student.get("gender", "") or "").strip()

    criteria_total = 0
    criteria_met = 0
    fail_reasons = []
    pass_reasons = []

    # Marks criterion
    if "min_marks" in rules:
        criteria_total += 1
        if marks >= rules["min_marks"]:
            criteria_met += 1
            pass_reasons.append(f"Marks {marks}% meets minimum {rules['min_marks']}%")
        else:
            fail_reasons.append(f"Marks {marks}% below required {rules['min_marks']}%")

    # Income criterion
    if "max_income" in rules:
        criteria_total += 1
        if income <= rules["max_income"]:
            criteria_met += 1
            pass_reasons.append(f"Income ₹{income:,.0f} within limit ₹{rules['max_income']:,.0f}")
        else:
            fail_reasons.append(
                f"Income ₹{income:,.0f} exceeds limit ₹{rules['max_income']:,.0f} "
                f"by ₹{income - rules['max_income']:,.0f}"
            )

    # Category criterion
    if "category" in rules:
        criteria_total += 1
        if category.upper() in [c.upper() for c in rules["category"]]:
            criteria_met += 1
            pass_reasons.append(f"Category '{category}' matches requirement")
        else:
            fail_reasons.append(
                f"Category '{category}' does not match required category "
                f"({', '.join(rules['category'])})"
            )

    # Minority category criterion
    if "minority_categories" in rules:
        criteria_total += 1
        if _is_minority(category):
            criteria_met += 1
            pass_reasons.append(f"Category '{category}' qualifies as minority")
        else:
            fail_reasons.append(f"Category '{category}' is not a recognized minority category")

    # Degree level criterion (undergraduate)
    if "degree_levels" in rules:
        criteria_total += 1
        if _is_undergraduate(course):
            criteria_met += 1
            pass_reasons.append(f"Course '{course}' is an undergraduate degree")
        else:
            fail_reasons.append(f"Course '{course}' is not an undergraduate degree")

    # Technical course criterion
    if "technical_courses" in rules:
        criteria_total += 1
        if _is_technical_course(course):
            criteria_met += 1
            pass_reasons.append(f"Course '{course}' is a technical course")
        else:
            fail_reasons.append(f"Course '{course}' is not a recognized technical course")

    # Gender criterion
    if "gender" in rules:
        criteria_total += 1
        if gender.lower() == rules["gender"].lower():
            criteria_met += 1
            pass_reasons.append(f"Gender '{gender}' matches requirement")
        else:
            fail_reasons.append(f"Gender '{gender}' does not match required '{rules['gender']}'")

    eligible = criteria_total > 0 and criteria_met == criteria_total

    # Match score: base proportion of criteria met, scaled to 0-100,
    # with small bonus for margin on numeric criteria (income/marks headroom)
    base_score = (criteria_met / criteria_total * 100) if criteria_total else 0

    bonus = 0
    if "min_marks" in rules and marks >= rules["min_marks"]:
        bonus += min(5, (marks - rules["min_marks"]) / 4)
    if "max_income" in rules and income <= rules["max_income"]:
        headroom = rules["max_income"] - income
        bonus += min(5, headroom / max(rules["max_income"], 1) * 10)

    match_score = round(min(100, base_score + bonus), 1)

    if eligible:
        reason = "Eligible: " + "; ".join(pass_reasons)
    else:
        reason = "Not eligible: " + "; ".join(fail_reasons)

    return {
        "name": name,
        "provider": scheme["provider"],
        "match_score": match_score,
        "eligible": eligible,
        "reason": reason
    }


def recommend_scholarships(student_data: dict) -> list:
    """
    Given a student's profile, return a ranked list of scholarship
    recommendations with match scores, eligibility, and reasons.

    student_data keys used:
        income, marks, category, course, gender
    """
    results = [_score_scholarship(scheme, student_data) for scheme in SCHOLARSHIP_SCHEMES]

    # Rank: eligible first, then by match score descending
    results.sort(key=lambda r: (r["eligible"], r["match_score"]), reverse=True)

    return results


def get_top_recommendation(student_data: dict) -> dict:
    """Return the single best-matching scholarship (eligible preferred)."""
    recs = recommend_scholarships(student_data)
    return recs[0] if recs else None
