"""
AI-Powered Rejection/Review/Suspicion Explanation Generator.

Produces human-readable explanations for why an application received
a given status, based on eligibility results, document match scores,
and flags raised during processing.
"""


def generate_explanation(eligibility_result: dict, match_scores: dict, flags: list, status: str) -> dict:
    """
    Generate a structured, human-readable explanation for the application's
    classification status.

    Returns:
        {
            "status": "Rejected" | "Needs Review" | "Suspicious" | "Approved",
            "summary": "...",
            "reasons": ["...", "..."]
        }
    """
    reasons = []

    income_info = eligibility_result.get("income", {})
    marks_info = eligibility_result.get("marks", {})
    course_info = eligibility_result.get("course", {})
    category_info = eligibility_result.get("category", {})

    name_score = match_scores.get("name_match", 100)
    dob_score = match_scores.get("dob_match", 100)
    income_score = match_scores.get("income_match", 100)
    bank_score = match_scores.get("bank_match", 100)

    if status == "Approved":
        summary = "Application approved — all eligibility and verification checks passed."
        reasons.append(
            f"Eligibility criteria met (income, marks, course, category all within limits)."
        )
        reasons.append(
            f"Document verification scores are strong "
            f"(name {name_score}%, DOB {dob_score}%, income {income_score}%, bank {bank_score}%)."
        )
        return {"status": status, "summary": summary, "reasons": reasons}

    if status == "Rejected":
        summary = "Rejected because:"

        if income_info and not income_info.get("pass", True):
            value = income_info.get("value", 0)
            limit = income_info.get("limit", 0)
            diff = value - limit
            reasons.append(
                f"Family income exceeds the scholarship limit by ₹{diff:,.0f} "
                f"(income ₹{value:,.0f} vs limit ₹{limit:,.0f})"
            )

        if marks_info and not marks_info.get("pass", True):
            value = marks_info.get("value", 0)
            minimum = marks_info.get("min", 0)
            reasons.append(
                f"Marks below required threshold "
                f"(scored {value}%, minimum required {minimum}%)"
            )

        if course_info and not course_info.get("pass", True):
            reasons.append(f"Course '{course_info.get('value', '')}' is not an eligible course")

        if category_info and not category_info.get("pass", True):
            reasons.append(f"Category '{category_info.get('value', '')}' is not a recognized category")

        if not reasons:
            reasons.append("Application does not meet one or more eligibility criteria.")

        return {"status": status, "summary": summary, "reasons": reasons}

    if status == "Needs Review":
        summary = "Needs Review because:"

        if name_score < 70:
            reasons.append(f"Name similarity only {name_score}% between form and documents")

        if dob_score < 80:
            reasons.append(f"Date of birth match only {dob_score}% between form and documents")

        if income_score < 65:
            reasons.append(f"Income figure match only {income_score}% between form and documents")

        if bank_score < 60:
            reasons.append(f"Bank account details match only {bank_score}% — needs manual verification")

        for flag in flags:
            if flag not in reasons:
                reasons.append(flag)

        if not reasons:
            reasons.append("Minor inconsistencies detected between submitted form and documents.")

        return {"status": status, "summary": summary, "reasons": reasons}

    if status == "Suspicious":
        summary = "Suspicious because:"

        for flag in flags:
            if "duplicate" in flag.lower():
                if "bank" in flag.lower():
                    reasons.append("Duplicate bank account found across applications")
                elif "aadhaar" in flag.lower():
                    reasons.append("Duplicate Aadhaar number detected across applications")
                else:
                    reasons.append(flag)

        if name_score < 60:
            reasons.append(f"Major document mismatch detected — name similarity only {name_score}%")

        if income_score < 50:
            reasons.append(f"Major document mismatch detected — income figures only {income_score}% consistent")

        for flag in flags:
            if flag not in reasons and "duplicate" not in flag.lower():
                reasons.append(flag)

        if not reasons:
            reasons.append("Significant inconsistencies suggest the application requires investigation.")

        return {"status": status, "summary": summary, "reasons": reasons}

    # Fallback for any unrecognized status
    return {
        "status": status,
        "summary": f"Application status: {status}",
        "reasons": flags or ["No specific issues recorded."]
    }
