from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'))
    doc_type = db.Column(db.String(50))
    filepath = db.Column(db.String(200))
    extracted_text = db.Column(db.Text)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    dob = db.Column(db.String(20))
    aadhaar = db.Column(db.String(20))
    category = db.Column(db.String(20))
    income = db.Column(db.Float)
    marks = db.Column(db.Float)
    course = db.Column(db.String(100))
    year = db.Column(db.Integer)
    bank_account = db.Column(db.String(30))
    bank_name = db.Column(db.String(100))
    status = db.Column(db.String(30), default='Needs Review')
    confidence = db.Column(db.Float, default=0.0)
    flags = db.Column(db.Text, default='[]')
    eligibility_result = db.Column(db.Text)
    match_scores = db.Column(db.Text)
    duplicate_flag = db.Column(db.Boolean, default=False)
    duplicate_reason = db.Column(db.String(200))
    created_at = db.Column(db.DateTime)
    documents = db.relationship('Document', backref='application', lazy=True)
