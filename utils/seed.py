"""
Demo data seeder.

Populates the database with realistic sample applications, computing
eligibility results, scholarship recommendations, eligibility scores,
and AI explanations the same way process_application() does in app.py,
so that every seeded record renders correctly on the dashboard and
detail pages.
"""
import json
from datetime import datetime

from utils.eligibility import check_eligibility, calculate_eligibility_score
from utils.scholarship_recommender import get_top_recommendation
from utils.explainer import generate_explanation


def seed_data(db):
    from models.database import Application

    demo_apps = [
        {
            'name': 'Priya Shankar', 'gender': 'Female', 'dob': '2002-05-14',
            'aadhaar': '1234-5678-9012', 'category': 'SC', 'income': 180000,
            'marks': 87.5, 'course': 'B.Tech Computer Science', 'year': 2,
            'bank_account': '31245678901', 'bank_name': 'SBI',
            'status': 'Approved', 'confidence': 92.4,
            'flags': [],
            'match_scores': {"name_match": 95, "dob_match": 100, "income_match": 88, "bank_match": 85, "overall": 93}
        },
        {
            'name': 'M. Ravi Kumar', 'gender': 'Male', 'dob': '2001-11-22',
            'aadhaar': '2345-6789-0123', 'category': 'OBC', 'income': 140000,
            'marks': 72.0, 'course': 'B.Sc Mathematics', 'year': 3,
            'bank_account': '42356789012', 'bank_name': 'Canara Bank',
            'status': 'Approved', 'confidence': 88.1,
            'flags': [],
            'match_scores': {"name_match": 88, "dob_match": 100, "income_match": 91, "bank_match": 78, "overall": 90}
        },
        {
            'name': 'Deepa R', 'gender': 'Female', 'dob': '2003-07-09',
            'aadhaar': '3456-7890-1234', 'category': 'EWS', 'income': 620000,
            'marks': 91.0, 'course': 'MBBS', 'year': 1,
            'bank_account': '53467890123', 'bank_name': 'HDFC',
            'status': 'Needs Review', 'confidence': 61.5,
            'flags': ["Income figure discrepancy across documents (62% match)"],
            'match_scores': {"name_match": 82, "dob_match": 100, "income_match": 62, "bank_match": 71, "overall": 78}
        },
        {
            'name': 'Karthik Selvam', 'gender': 'Male', 'dob': '2000-03-17',
            'aadhaar': '4567-8901-2345', 'category': 'General', 'income': 850000,
            'marks': 68.5, 'course': 'B.Com', 'year': 2,
            'bank_account': '64578901234', 'bank_name': 'IOB',
            'status': 'Rejected', 'confidence': 5.0,
            'flags': ["Income exceeds eligibility limit for category", "Marks below minimum threshold for category"],
            'match_scores': {"name_match": 91, "dob_match": 100, "income_match": 85, "bank_match": 80, "overall": 90}
        },
        {
            'name': 'Anitha Devi', 'gender': 'Female', 'dob': '2002-08-25',
            'aadhaar': '5678-9012-3456', 'category': 'ST', 'income': 95000,
            'marks': 61.0, 'course': 'B.Tech Electronics', 'year': 1,
            'bank_account': '75689012345', 'bank_name': 'SBI',
            'status': 'Suspicious', 'confidence': 12.0,
            'flags': ["Name mismatch detected (48% similarity)", "Possible duplicate application detected"],
            'match_scores': {"name_match": 48, "dob_match": 85, "income_match": 70, "bank_match": 55, "overall": 65}
        },
        {
            'name': 'Suresh Babu', 'gender': 'Male', 'dob': '1999-12-01',
            'aadhaar': '6789-0123-4567', 'category': 'OBC', 'income': 125000,
            'marks': 79.5, 'course': 'MBA', 'year': 1,
            'bank_account': '86790123456', 'bank_name': 'Punjab National Bank',
            'status': 'Approved', 'confidence': 90.3,
            'flags': [],
            'match_scores': {"name_match": 94, "dob_match": 100, "income_match": 87, "bank_match": 82, "overall": 91}
        },
        {
            'name': 'Lakshmi Priya', 'gender': 'Female', 'dob': '2001-04-30',
            'aadhaar': '7890-1234-5678', 'category': 'SC', 'income': 210000,
            'marks': 55.0, 'course': 'BA English', 'year': 2,
            'bank_account': '97801234567', 'bank_name': 'Indian Bank',
            'status': 'Needs Review', 'confidence': 67.8,
            'flags': ["Bank account details unclear (58% match)"],
            'match_scores': {"name_match": 79, "dob_match": 100, "income_match": 83, "bank_match": 58, "overall": 80}
        },
        {
            'name': 'Vijay Mohan', 'gender': 'Male', 'dob': '2002-09-11',
            'aadhaar': '8901-2345-6789', 'category': 'EWS', 'income': 520000,
            'marks': 83.0, 'course': 'B.Tech Mechanical', 'year': 4,
            'bank_account': '08912345678', 'bank_name': 'Axis Bank',
            'status': 'Approved', 'confidence': 86.5,
            'flags': [],
            'match_scores': {"name_match": 93, "dob_match": 100, "income_match": 88, "bank_match": 77, "overall": 91}
        },
    ]

    for d in demo_apps:
        # 1. Eligibility check (same shape as app.py)
        eligibility_result = check_eligibility({
            'income': d['income'],
            'marks': d['marks'],
            'category': d['category'],
            'course': d['course'],
            'year': d['year'],
        })

        # 2. Scholarship recommendation
        profile = {
            'income': d['income'],
            'marks': d['marks'],
            'category': d['category'],
            'course': d['course'],
            'gender': d['gender'],
        }
        top = get_top_recommendation(profile)

        # 3. Eligibility score (out of 100)
        score_input = dict(profile)
        score_input['match_scores'] = d['match_scores']
        eligibility_score = calculate_eligibility_score(score_input)

        # 4. AI explanation
        explanation = generate_explanation(
            eligibility_result, d['match_scores'], d['flags'], d['status']
        )

        app_obj = Application(
            name=d['name'], dob=d['dob'], aadhaar=d['aadhaar'],
            category=d['category'], gender=d['gender'],
            income=d['income'], marks=d['marks'],
            course=d['course'], year=d['year'],
            bank_account=d['bank_account'], bank_name=d['bank_name'],

            status=d['status'], confidence=d['confidence'],
            flags=json.dumps(d['flags']),
            match_scores=json.dumps(d['match_scores']),
            eligibility_result=json.dumps(eligibility_result),

            duplicate_flag=('Suspicious' in d['status']),
            duplicate_reason=(
                "Similar applicant profile flagged during demo seeding"
                if 'Suspicious' in d['status'] else None
            ),

            recommended_scholarship=top['name'] if top else None,
            recommendation_score=top['match_score'] if top else None,
            eligibility_score=eligibility_score['score'],
            explanation=json.dumps(explanation),

            created_at=datetime.utcnow()
        )
        db.session.add(app_obj)

    db.session.commit()