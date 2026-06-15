"""
Scholarship Deadline Tracker.

Maintains metadata about scholarship schemes (provider, deadline,
benefit amount) and provides helpers to retrieve active scholarships
sorted by nearest deadline.
"""
from datetime import datetime

SCHOLARSHIP_DEADLINES = [
    {
        "scholarship_name": "Central Sector Scholarship",
        "provider": "Ministry of Education, Govt. of India",
        "deadline": "2026-10-31",
        "benefit_amount": "₹12,000 / year"
    },
    {
        "scholarship_name": "Post Matric Scholarship (SC)",
        "provider": "Ministry of Social Justice & Empowerment",
        "deadline": "2026-09-30",
        "benefit_amount": "Up to ₹20,000 / year"
    },
    {
        "scholarship_name": "Post Matric Scholarship (ST)",
        "provider": "Ministry of Tribal Affairs",
        "deadline": "2026-09-30",
        "benefit_amount": "Up to ₹20,000 / year"
    },
    {
        "scholarship_name": "Merit-cum-Means Scholarship",
        "provider": "Ministry of Minority Affairs",
        "deadline": "2026-11-15",
        "benefit_amount": "Up to ₹20,000 / year (tuition + maintenance)"
    },
    {
        "scholarship_name": "AICTE Pragati Scholarship",
        "provider": "AICTE",
        "deadline": "2026-12-31",
        "benefit_amount": "₹50,000 / year"
    },
]


def get_active_scholarships(reference_date: datetime = None) -> list:
    """
    Return scholarships whose deadline has not yet passed,
    sorted by nearest deadline first.

    If reference_date is not provided, the current date/time is used.
    """
    if reference_date is None:
        reference_date = datetime.utcnow()

    active = []
    for s in SCHOLARSHIP_DEADLINES:
        try:
            deadline_dt = datetime.strptime(s["deadline"], "%Y-%m-%d")
        except ValueError:
            continue
        if deadline_dt >= reference_date:
            entry = dict(s)
            entry["days_remaining"] = (deadline_dt - reference_date).days
            active.append(entry)

    active.sort(key=lambda s: s["deadline"])
    return active


def get_all_scholarships() -> list:
    """Return all known scholarship metadata, sorted by deadline."""
    return sorted(SCHOLARSHIP_DEADLINES, key=lambda s: s["deadline"])
