SCHOLARSHIP_RULES = {
    'SC': {'income_limit': 250000, 'min_marks': 50},
    'ST': {'income_limit': 250000, 'min_marks': 50},
    'OBC': {'income_limit': 150000, 'min_marks': 55},
    'EWS': {'income_limit': 800000, 'min_marks': 60},
    'General': {'income_limit': 600000, 'min_marks': 75},
}

ELIGIBLE_COURSES = [
    'B.Tech', 'B.E.', 'B.Sc', 'B.Com', 'BA', 'BBA',
    'M.Tech', 'M.Sc', 'MBA', 'MCA', 'MBBS', 'BCA',
    'Diploma', 'Polytechnic'
]

MAX_YEAR = 4


def check_eligibility(data: dict) -> dict:
    """
    Rule-based eligibility check.
    Returns a dict with pass/fail per criterion and overall decision.
    """
    category = data.get('category', 'General')
    income = float(data.get('income', 0))
    marks = float(data.get('marks', 0))
    course = data.get('course', '')
    year = int(data.get('year', 1))

    rules = SCHOLARSHIP_RULES.get(category, SCHOLARSHIP_RULES['General'])

    results = {}

    # Income check
    income_ok = income <= rules['income_limit']
    results['income'] = {
        'pass': income_ok,
        'value': income,
        'limit': rules['income_limit'],
        'message': f"Annual income ₹{income:,.0f} {'≤' if income_ok else '>'} limit ₹{rules['income_limit']:,.0f}"
    }

    # Marks check
    marks_ok = marks >= rules['min_marks']
    results['marks'] = {
        'pass': marks_ok,
        'value': marks,
        'min': rules['min_marks'],
        'message': f"Marks {marks}% {'≥' if marks_ok else '<'} minimum {rules['min_marks']}%"
    }

    # Course check
    course_ok = any(c.lower() in course.lower() for c in ELIGIBLE_COURSES) or len(course) > 2
    results['course'] = {
        'pass': course_ok,
        'value': course,
        'message': f"Course '{course}' {'is' if course_ok else 'is not'} in eligible list"
    }

    # Year check
    year_ok = 1 <= year <= MAX_YEAR
    results['year'] = {
        'pass': year_ok,
        'value': year,
        'message': f"Year {year} {'is' if year_ok else 'is not'} within valid range (1-{MAX_YEAR})"
    }

    # Category check
    category_ok = category in SCHOLARSHIP_RULES
    results['category'] = {
        'pass': category_ok,
        'value': category,
        'message': f"Category '{category}' {'is' if category_ok else 'is not'} a recognized category"
    }

    overall = all(r['pass'] for r in results.values())
    results['overall'] = overall

    return results
