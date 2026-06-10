from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os, json
from utils.ocr_engine import extract_text_from_image
from utils.matcher import compute_match_scores, detect_duplicates
from utils.eligibility import check_eligibility
from utils.classifier import classify_application
from models.database import db, Application, Document

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scholarship.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'sih-scholarship-key-2024'

db.init_app(app)

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
    return render_template('dashboard.html',
        total=total, approved=approved, rejected=rejected,
        review=review, suspicious=suspicious, applications=apps)

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
        income=float(data.get('income', 0)),
        marks=float(data.get('marks', 0)),
        course=data.get('course', ''),
        year=int(data.get('year', 1)),
        bank_account=data.get('bank_account', ''),
        bank_name=data.get('bank_name', ''),
        created_at=datetime.utcnow()
    )

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

    eligibility = check_eligibility({
        'income': app_obj.income,
        'marks': app_obj.marks,
        'category': app_obj.category,
        'course': app_obj.course,
        'year': app_obj.year
    })

    match_scores = compute_match_scores(data, extracted_data)
    duplicate_flag, dup_reason = detect_duplicates(app_obj, db)
    status, confidence, flags = classify_application(eligibility, match_scores, duplicate_flag)

    app_obj.status = status
    app_obj.confidence = confidence
    app_obj.flags = json.dumps(flags)
    app_obj.eligibility_result = json.dumps(eligibility)
    app_obj.match_scores = json.dumps(match_scores)
    app_obj.duplicate_flag = duplicate_flag
    app_obj.duplicate_reason = dup_reason

    db.session.add(app_obj)
    db.session.commit()

    return redirect(url_for('result', app_id=app_obj.id))

@app.route('/result/<int:app_id>')
def result(app_id):
    app_obj = Application.query.get_or_404(app_id)
    flags = json.loads(app_obj.flags or '[]')
    eligibility = json.loads(app_obj.eligibility_result or '{}')
    match_scores = json.loads(app_obj.match_scores or '{}')
    return render_template('result.html', app=app_obj, flags=flags,
                           eligibility=eligibility, match_scores=match_scores)

@app.route('/application/<int:app_id>')
def application_detail(app_id):
    app_obj = Application.query.get_or_404(app_id)
    flags = json.loads(app_obj.flags or '[]')
    eligibility = json.loads(app_obj.eligibility_result or '{}')
    match_scores = json.loads(app_obj.match_scores or '{}')
    return render_template('detail.html', app=app_obj, flags=flags,
                           eligibility=eligibility, match_scores=match_scores)

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
        'duplicate': a.duplicate_flag, 'created_at': str(a.created_at)
    } for a in apps])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
