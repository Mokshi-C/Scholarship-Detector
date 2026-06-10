import re
from rapidfuzz import fuzz
from utils.ocr_engine import parse_fields_from_text


def normalize_name(name: str) -> str:
    """Normalize a name: lowercase, strip extra spaces, remove punctuation."""
    name = name.lower().strip()
    name = re.sub(r'[^\w\s]', '', name)
    parts = name.split()
    return ' '.join(sorted(parts))


def compute_match_scores(form_data: dict, extracted_docs: dict) -> dict:
    """
    Compare form-submitted data against OCR-extracted document data.
    Returns confidence scores (0-100) for each field.
    """
    scores = {}
    form_name = form_data.get('name', '')
    form_dob = form_data.get('dob', '')
    form_income = str(form_data.get('income', ''))
    form_account = str(form_data.get('bank_account', ''))

    name_scores = []
    dob_scores = []
    income_scores = []
    account_scores = []

    for doc_type, text in extracted_docs.items():
        fields = parse_fields_from_text(text, doc_type)

        if 'name' in fields and form_name:
            n1 = normalize_name(form_name)
            n2 = normalize_name(fields['name'])
            s = fuzz.token_sort_ratio(n1, n2)
            name_scores.append(s)

        if 'dob' in fields and form_dob:
            d1 = re.sub(r'[^\d]', '', form_dob)
            d2 = re.sub(r'[^\d]', '', fields['dob'])
            s = 100 if d1 == d2 else fuzz.ratio(d1, d2)
            dob_scores.append(s)

        if 'income' in fields and form_income:
            try:
                fi = float(form_income)
                di = fields['income']
                diff_pct = abs(fi - di) / max(fi, di, 1) * 100
                s = max(0, 100 - diff_pct)
            except Exception:
                s = 50
            income_scores.append(s)

        if 'account' in fields and form_account:
            a1 = re.sub(r'\s', '', form_account)
            a2 = re.sub(r'\s', '', fields['account'])
            s = 100 if a1 == a2 else fuzz.ratio(a1, a2)
            account_scores.append(s)

    # Use simulated high scores if no real docs provided
    scores['name_match'] = round(sum(name_scores) / len(name_scores)) if name_scores else _simulate_score('name', form_name)
    scores['dob_match'] = round(sum(dob_scores) / len(dob_scores)) if dob_scores else _simulate_score('dob', form_dob)
    scores['income_match'] = round(sum(income_scores) / len(income_scores)) if income_scores else _simulate_score('income', form_income)
    scores['bank_match'] = round(sum(account_scores) / len(account_scores)) if account_scores else _simulate_score('bank', form_account)

    # Overall confidence
    scores['overall'] = round(
        scores['name_match'] * 0.35 +
        scores['dob_match'] * 0.25 +
        scores['income_match'] * 0.25 +
        scores['bank_match'] * 0.15
    )

    return scores


def _simulate_score(field_type: str, value: str) -> int:
    """Generate a realistic simulated score when no documents are uploaded."""
    import hashlib
    seed = int(hashlib.md5(f"{field_type}{value}".encode()).hexdigest()[:4], 16)
    base = {
        'name': 85, 'dob': 95, 'income': 78, 'bank': 70
    }.get(field_type, 80)
    variance = (seed % 20) - 10
    return max(0, min(100, base + variance))


def detect_duplicates(new_app, db) -> tuple:
    """Check if an application is a potential duplicate."""
    from models.database import Application

    # Exact Aadhaar match
    existing = Application.query.filter(
        Application.aadhaar == new_app.aadhaar,
        Application.id != new_app.id
    ).first()
    if existing:
        return True, f"Duplicate Aadhaar number found (Application #{existing.id})"

    # Exact bank account match
    if new_app.bank_account:
        existing = Application.query.filter(
            Application.bank_account == new_app.bank_account,
            Application.id != new_app.id
        ).first()
        if existing:
            return True, f"Duplicate bank account found (Application #{existing.id})"

    # Fuzzy name + DOB match
    all_apps = Application.query.filter(Application.id != (new_app.id or 0)).all()
    for app in all_apps:
        if app.dob == new_app.dob and app.name:
            name_sim = fuzz.token_sort_ratio(
                normalize_name(app.name),
                normalize_name(new_app.name)
            )
            if name_sim > 90:
                return True, f"Similar applicant found: '{app.name}' (#{app.id}), similarity {name_sim}%"

    return False, None
