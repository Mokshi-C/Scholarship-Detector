from datetime import datetime
import json


def seed_data(db):
    from models.database import Application

    demo_apps = [
        {
            'name': 'Priya Shankar', 'dob': '2002-05-14', 'aadhaar': '1234-5678-9012',
            'category': 'SC', 'income': 180000, 'marks': 87.5,
            'course': 'B.Tech Computer Science', 'year': 2,
            'bank_account': '31245678901', 'bank_name': 'SBI',
            'status': 'Approved', 'confidence': 92.4,
            'flags': '[]',
            'match_scores': '{"name_match":95,"dob_match":100,"income_match":88,"bank_match":85,"overall":93}',
            'eligibility_result': '{"overall":true,"income":{"pass":true},"marks":{"pass":true},"course":{"pass":true},"year":{"pass":true},"category":{"pass":true}}'
        },
        {
            'name': 'M. Ravi Kumar', 'dob': '2001-11-22', 'aadhaar': '2345-6789-0123',
            'category': 'OBC', 'income': 140000, 'marks': 72.0,
            'course': 'B.Sc Mathematics', 'year': 3,
            'bank_account': '42356789012', 'bank_name': 'Canara Bank',
            'status': 'Approved', 'confidence': 88.1,
            'flags': '[]',
            'match_scores': '{"name_match":88,"dob_match":100,"income_match":91,"bank_match":78,"overall":90}',
            'eligibility_result': '{"overall":true,"income":{"pass":true},"marks":{"pass":true},"course":{"pass":true},"year":{"pass":true},"category":{"pass":true}}'
        },
        {
            'name': 'Deepa R', 'dob': '2003-07-09', 'aadhaar': '3456-7890-1234',
            'category': 'EWS', 'income': 620000, 'marks': 91.0,
            'course': 'MBBS', 'year': 1,
            'bank_account': '53467890123', 'bank_name': 'HDFC',
            'status': 'Needs Review', 'confidence': 61.5,
            'flags': '["Income figure discrepancy across documents (62% match)"]',
            'match_scores': '{"name_match":82,"dob_match":100,"income_match":62,"bank_match":71,"overall":78}',
            'eligibility_result': '{"overall":true,"income":{"pass":true},"marks":{"pass":true},"course":{"pass":true},"year":{"pass":true},"category":{"pass":true}}'
        },
        {
            'name': 'Karthik Selvam', 'dob': '2000-03-17', 'aadhaar': '4567-8901-2345',
            'category': 'General', 'income': 850000, 'marks': 68.5,
            'course': 'B.Com', 'year': 2,
            'bank_account': '64578901234', 'bank_name': 'IOB',
            'status': 'Rejected', 'confidence': 5.0,
            'flags': '["Income exceeds eligibility limit for category","Marks below minimum threshold for category"]',
            'match_scores': '{"name_match":91,"dob_match":100,"income_match":85,"bank_match":80,"overall":90}',
            'eligibility_result': '{"overall":false,"income":{"pass":false},"marks":{"pass":false},"course":{"pass":true},"year":{"pass":true},"category":{"pass":true}}'
        },
        {
            'name': 'Anitha Devi', 'dob': '2002-08-25', 'aadhaar': '5678-9012-3456',
            'category': 'ST', 'income': 95000, 'marks': 61.0,
            'course': 'B.Tech Electronics', 'year': 1,
            'bank_account': '75689012345', 'bank_name': 'SBI',
            'status': 'Suspicious', 'confidence': 12.0,
            'flags': '["Name mismatch detected (48% similarity)","Possible duplicate application detected"]',
            'match_scores': '{"name_match":48,"dob_match":85,"income_match":70,"bank_match":55,"overall":65}',
            'eligibility_result': '{"overall":true,"income":{"pass":true},"marks":{"pass":true},"course":{"pass":true},"year":{"pass":true},"category":{"pass":true}}'
        },
        {
            'name': 'Suresh Babu', 'dob': '1999-12-01', 'aadhaar': '6789-0123-4567',
            'category': 'OBC', 'income': 125000, 'marks': 79.5,
            'course': 'MBA', 'year': 1,
            'bank_account': '86790123456', 'bank_name': 'Punjab National Bank',
            'status': 'Approved', 'confidence': 90.3,
            'flags': '[]',
            'match_scores': '{"name_match":94,"dob_match":100,"income_match":87,"bank_match":82,"overall":91}',
            'eligibility_result': '{"overall":true,"income":{"pass":true},"marks":{"pass":true},"course":{"pass":true},"year":{"pass":true},"category":{"pass":true}}'
        },
        {
            'name': 'Lakshmi Priya', 'dob': '2001-04-30', 'aadhaar': '7890-1234-5678',
            'category': 'SC', 'income': 210000, 'marks': 55.0,
            'course': 'BA English', 'year': 2,
            'bank_account': '97801234567', 'bank_name': 'Indian Bank',
            'status': 'Needs Review', 'confidence': 67.8,
            'flags': '["Bank account details unclear (58% match)"]',
            'match_scores': '{"name_match":79,"dob_match":100,"income_match":83,"bank_match":58,"overall":80}',
            'eligibility_result': '{"overall":true,"income":{"pass":true},"marks":{"pass":true},"course":{"pass":true},"year":{"pass":true},"category":{"pass":true}}'
        },
        {
            'name': 'Vijay Mohan', 'dob': '2002-09-11', 'aadhaar': '8901-2345-6789',
            'category': 'EWS', 'income': 520000, 'marks': 83.0,
            'course': 'B.Tech Mechanical', 'year': 4,
            'bank_account': '08912345678', 'bank_name': 'Axis Bank',
            'status': 'Approved', 'confidence': 86.5,
            'flags': '[]',
            'match_scores': '{"name_match":93,"dob_match":100,"income_match":88,"bank_match":77,"overall":91}',
            'eligibility_result': '{"overall":true,"income":{"pass":true},"marks":{"pass":true},"course":{"pass":true},"year":{"pass":true},"category":{"pass":true}}'
        },
    ]

    for d in demo_apps:
        app = Application(
            name=d['name'], dob=d['dob'], aadhaar=d['aadhaar'],
            category=d['category'], income=d['income'], marks=d['marks'],
            course=d['course'], year=d['year'],
            bank_account=d['bank_account'], bank_name=d['bank_name'],
            status=d['status'], confidence=d['confidence'],
            flags=d['flags'], match_scores=d['match_scores'],
            eligibility_result=d['eligibility_result'],
            duplicate_flag='Suspicious' in d['status'],
            created_at=datetime.utcnow()
        )
        db.session.add(app)
    db.session.commit()
