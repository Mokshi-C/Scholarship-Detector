from utils.chatbot import ask_scholarbot
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os, json
from utils.ocr_engine import extract_text_from_image
from utils.matcher import compute_match_scores, detect_duplicates
from utils.eligibility import check_eligibility, calculate_eligibility_score
from utils.classifier import classify_application
from utils.scholarship_recommender import recommend_scholarships
from utils.explainer import generate_explanation
from utils.deadlines import get_active_scholarships
from models.database import db, Application, Document
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("Gemini Key:", os.getenv("GEMINI_API_KEY"))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scholarship.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'sih-scholarship-key-2024'

# Make sure the uploads folder exists (fresh clones won't have it)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)


@app.template_filter('from_json')
def from_json_filter(value):
    """Safely parse a JSON text column for use in templates."""
    if not value:
        return {}
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return {}


with app.app_context():
    db.create_all()
    # Seed demo data
    if Application.query.count() == 0:
        from utils.seed import seed_data
        seed_data(db)


@app.route('/')
def dashboard():
    total = Application.query.count()
    approved = Application.query.filter_by(status='Approved').count()
    rejected = Application.query.filter_by(status='Rejected').count()
    review = Application.query.filter_by(status='Needs Review').count()
    suspicious = Application.query.filter_by(status='Suspicious').count()
    apps = Application.query.order_by(Application.created_at.desc()).limit(20).all()
    upcoming_deadlines = get_active_scholarships()[:5]
    return render_template('dashboard.html',
        total=total, approved=approved, rejected=rejected,
        review=review, suspicious=suspicious, applications=apps,
        upcoming_deadlines=upcoming_deadlines)


@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        return process_application(request)
    return render_template('apply.html')


def process_application(req):
    data = req.form
    files = req.files

    app_obj = Application(
        name=data.get('name', ''),
        dob=data.get('dob', ''),
        aadhaar=data.get('aadhaar', ''),
        category=data.get('category', ''),
        income=float(data.get('income', 0) or 0),
        marks=float(data.get('marks', 0) or 0),
        course=data.get('course', ''),
        year=int(data.get('year', 1) or 1),
        bank_account=data.get('bank_account', ''),
        bank_name=data.get('bank_name', ''),
        gender=data.get('gender', ''),
        created_at=datetime.utcnow()
    )

    # --- 1. OCR + field extraction ---
    extracted_data = {}
    doc_types = ['aadhaar', 'marksheet', 'income_certificate', 'bank_passbook']
    for doc_type in doc_types:
        if doc_type in files and files[doc_type].filename:
            file = files[doc_type]
            filepath = os.path.join('uploads', f"{data.get('aadhaar', 'unknown')}_{doc_type}_{file.filename}")
            file.save(filepath)
            text = extract_text_from_image(filepath)
            extracted_data[doc_type] = text
            doc = Document(doc_type=doc_type, filepath=filepath, extracted_text=text)
            app_obj.documents.append(doc)

    # --- 2. Eligibility check ---
    eligibility = check_eligibility({
        'income': app_obj.income,
        'marks': app_obj.marks,
        'category': app_obj.category,
        'course': app_obj.course,
        'year': app_obj.year
    })

    # --- Document matching + duplicate detection ---
    match_scores = compute_match_scores(data, extracted_data)
    duplicate_flag, dup_reason = detect_duplicates(app_obj, db)
    status, confidence, flags = classify_application(eligibility, match_scores, duplicate_flag)

    # --- 3. Scholarship recommendation ---
    student_profile = {
        'income': app_obj.income,
        'marks': app_obj.marks,
        'category': app_obj.category,
        'course': app_obj.course,
        'gender': app_obj.gender,
    }
    recommendations = recommend_scholarships(student_profile)
    top_recommendation = recommendations[0] if recommendations else None

    # --- 4. Eligibility score ---
    score_input = dict(student_profile)
    score_input['match_scores'] = match_scores
    eligibility_score = calculate_eligibility_score(score_input)

    # --- 5. AI explanation ---
    explanation = generate_explanation(eligibility, match_scores, flags, status)

    # --- Persist everything ---
    app_obj.status = status
    app_obj.confidence = confidence
    app_obj.flags = json.dumps(flags)
    app_obj.eligibility_result = json.dumps(eligibility)
    app_obj.match_scores = json.dumps(match_scores)
    app_obj.duplicate_flag = duplicate_flag
    app_obj.duplicate_reason = dup_reason

    app_obj.recommended_scholarship = top_recommendation['name'] if top_recommendation else None
    app_obj.recommendation_score = top_recommendation['match_score'] if top_recommendation else None
    app_obj.eligibility_score = eligibility_score['score']
    app_obj.explanation = json.dumps(explanation)

    db.session.add(app_obj)
    db.session.commit()

    return redirect(url_for('result', app_id=app_obj.id))


@app.route('/result/<int:app_id>')
def result(app_id):
    app_obj = Application.query.get_or_404(app_id)
    flags = json.loads(app_obj.flags or '[]')
    eligibility = json.loads(app_obj.eligibility_result or '{}')
    match_scores = json.loads(app_obj.match_scores or '{}')
    explanation = json.loads(app_obj.explanation or '{}')
    return render_template('result.html', app=app_obj, flags=flags,
                           eligibility=eligibility, match_scores=match_scores,
                           explanation=explanation)


@app.route('/application/<int:app_id>')
def application_detail(app_id):
    app_obj = Application.query.get_or_404(app_id)
    flags = json.loads(app_obj.flags or '[]')
    eligibility = json.loads(app_obj.eligibility_result or '{}')
    match_scores = json.loads(app_obj.match_scores or '{}')
    explanation = json.loads(app_obj.explanation or '{}')

    student_profile = {
        'income': app_obj.income,
        'marks': app_obj.marks,
        'category': app_obj.category,
        'course': app_obj.course,
        'gender': app_obj.gender,
    }
    recommendations = recommend_scholarships(student_profile)

    return render_template('detail.html', app=app_obj, flags=flags,
                           eligibility=eligibility, match_scores=match_scores,
                           explanation=explanation, recommendations=recommendations)


@app.route('/api/update_status', methods=['POST'])
def update_status():
    data = request.json
    app_obj = Application.query.get(data['app_id'])
    if app_obj:
        app_obj.status = data['status']
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404


@app.route('/api/stats')
def stats():
    total = Application.query.count()
    by_status = db.session.execute(
        db.text("SELECT status, COUNT(*) FROM application GROUP BY status")
    ).fetchall()
    by_category = db.session.execute(
        db.text("SELECT category, COUNT(*) FROM application GROUP BY category")
    ).fetchall()
    return jsonify({
        'total': total,
        'by_status': [{'status': r[0], 'count': r[1]} for r in by_status],
        'by_category': [{'category': r[0], 'count': r[1]} for r in by_category]
    })


@app.route('/api/applications')
def api_applications():
    status_filter = request.args.get('status', '')
    query = Application.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    apps = query.order_by(Application.created_at.desc()).all()
    return jsonify([{
        'id': a.id, 'name': a.name, 'status': a.status,
        'confidence': a.confidence, 'category': a.category,
        'marks': a.marks, 'income': a.income, 'course': a.course,
        'duplicate': a.duplicate_flag, 'created_at': str(a.created_at),
        'recommended_scholarship': a.recommended_scholarship,
        'recommendation_score': a.recommendation_score,
        'eligibility_score': a.eligibility_score,
    } for a in apps])


@app.route('/api/deadlines')
def api_deadlines():
    return jsonify(get_active_scholarships())
@app.route('/api/chat', methods=['POST'])
def scholarbot_chat():

    data = request.json
    user_message = data.get('message', '')

    latest_application = Application.query.order_by(
        Application.created_at.desc()
    ).first()

    if not latest_application:
        return jsonify({
            "response": "No application data found. Please submit an application first."
        })

    student_profile = {
        'income': latest_application.income,
        'marks': latest_application.marks,
        'category': latest_application.category,
        'course': latest_application.course,
        'gender': latest_application.gender,
    }

    recommendations = recommend_scholarships(student_profile)

    scholarship_context = ""

    for s in recommendations:
        scholarship_context += f"""
        Scholarship Name: {s.get('name')}
        Match Score: {s.get('match_score')}
        Description: {s.get('description', '')}
        """

    student_context = f"""
    Student Name: {latest_application.name}

    Category: {latest_application.category}
    Gender: {latest_application.gender}
    Course: {latest_application.course}

    Annual Income: ₹{latest_application.income}

    Marks: {latest_application.marks}

    Eligibility Score: {latest_application.eligibility_score}

    Application Status: {latest_application.status}

    Recommended Scholarship:
    {latest_application.recommended_scholarship}
    """

    try:

        response = ask_scholarbot(
            user_message,
            scholarship_context,
            student_context
        )

        return jsonify({
            "response": response
        })

    except Exception as e:

        return jsonify({
            "response": f"Error: {str(e)}"
        }), 500
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)