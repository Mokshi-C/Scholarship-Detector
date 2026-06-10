# 🎓 ScholarVerify — Smart Scholarship Verification System
### SIH 2024 · ML + OCR Prototype

---

## 🚀 Quick Start

```bash
# 1. Clone / extract project
cd scholarship_system

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Tesseract OCR (for real OCR)
# Ubuntu/Debian:  sudo apt-get install tesseract-ocr
# macOS:          brew install tesseract
# Windows:        https://github.com/UB-Mannheim/tesseract/wiki

# 5. Run the app
python app.py
# Open: http://localhost:5000
```

---

## 🏗️ Project Structure

```
scholarship_system/
├── app.py                  # Flask app + routes
├── requirements.txt
├── models/
│   └── database.py         # SQLAlchemy models (Application, Document)
├── utils/
│   ├── ocr_engine.py       # Tesseract OCR + preprocessing
│   ├── matcher.py          # Fuzzy name/DOB/income matching (rapidfuzz)
│   ├── eligibility.py      # Rule-based eligibility checker
│   ├── classifier.py       # ML Random Forest classifier
│   └── seed.py             # Demo data seeder
├── templates/
│   ├── base.html           # Sidebar layout + nav
│   ├── dashboard.html      # Main overview + table
│   ├── apply.html          # Application form + upload
│   ├── detail.html         # Full review page
│   └── result.html         # Post-submission result
└── uploads/                # Saved document files
```

---

## 🤖 ML Features

### 1. Scholarship Eligibility Checker (Rule-Based)
Checks per category:
- **SC/ST**: Income ≤ ₹2.5L, marks ≥ 50%
- **OBC**: Income ≤ ₹1.5L, marks ≥ 55%
- **EWS**: Income ≤ ₹8L, marks ≥ 60%
- **General**: Income ≤ ₹6L, marks ≥ 75%

### 2. OCR Document Reader (pytesseract)
Extracts from: Aadhaar, Marksheet, Income Certificate, Bank Passbook

### 3. Mismatch Detection (rapidfuzz)
- **Name**: `fuzz.token_sort_ratio` — handles "Priya M" vs "M. Priya"
- **DOB**: Exact digit match + fuzzy fallback
- **Income**: % deviation scoring
- **Bank**: Exact then fuzzy match

### 4. Duplicate Detection
- Exact Aadhaar number match
- Exact bank account match
- Fuzzy name + same DOB (>90% similarity)

### 5. ML Classifier (Random Forest)
Features: `[income_ok, marks_ok, course_ok, year_ok, name_score, dob_score, income_score, bank_score, overall_score, duplicate_flag]`

Output: Approved / Rejected / Needs Review / Suspicious + confidence %

---

## 🖥️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Flask + Jinja2, custom CSS (no framework) |
| Backend | Python 3.11 + Flask |
| ML/NLP | scikit-learn, rapidfuzz |
| OCR | pytesseract + Pillow |
| Database | SQLite → PostgreSQL |
| Data | pandas, NumPy |

---

## 📊 Dashboard Features
- Filter by status (Approved / Rejected / Needs Review / Suspicious)
- Real-time search by name or Aadhaar
- Confidence bars per application
- Manual status override
- OCR text viewer
- Per-document match scores with visual bars

---

## 🔧 Extending to PostgreSQL

```python
# In app.py, replace:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scholarship.db'
# With:
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/scholardb'
# Then: pip install psycopg2-binary
```

---

## 🏆 SIH Demo Tips
1. Submit a new application without documents → system simulates OCR
2. Try submitting same Aadhaar twice → duplicate detection fires
3. Use name "M. Priya" when Aadhaar says "Priya M" → name mismatch flag
4. Set income above limit → rejected with explanation
5. Use dashboard filters to show review queue workflow
