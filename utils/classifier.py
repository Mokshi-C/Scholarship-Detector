"""
ML-based application classifier.
Uses a trained Random Forest on eligibility + match score features.
Falls back to rule-based logic for fresh installs.
"""
import os
import pickle
import numpy as np

MODEL_PATH = 'models/classifier.pkl'


def classify_application(eligibility: dict, match_scores: dict, duplicate_flag: bool) -> tuple:
    """
    Classify an application as: Approved, Rejected, Needs Review, or Suspicious.
    Returns: (status, confidence_score, flags_list)
    """
    flags = []

    # Feature engineering
    income_ok = eligibility.get('income', {}).get('pass', False)
    marks_ok = eligibility.get('marks', {}).get('pass', False)
    course_ok = eligibility.get('course', {}).get('pass', False)
    year_ok = eligibility.get('year', {}).get('pass', False)
    eligible = eligibility.get('overall', False)

    name_score = match_scores.get('name_match', 80)
    dob_score = match_scores.get('dob_match', 95)
    income_score = match_scores.get('income_match', 80)
    bank_score = match_scores.get('bank_match', 70)
    overall_match = match_scores.get('overall', 82)

    # Generate flags
    if name_score < 70:
        flags.append(f"Name mismatch detected ({name_score}% similarity)")
    if dob_score < 80:
        flags.append(f"Date of birth inconsistency ({dob_score}% match)")
    if income_score < 65:
        flags.append(f"Income figure discrepancy across documents ({income_score}% match)")
    if bank_score < 60:
        flags.append(f"Bank account details unclear ({bank_score}% match)")
    if duplicate_flag:
        flags.append("Possible duplicate application detected")
    if not income_ok:
        flags.append("Income exceeds eligibility limit for category")
    if not marks_ok:
        flags.append("Marks below minimum threshold for category")

    # Load ML model or use rule-based fallback
    model = _load_model()
    if model:
        features = np.array([[
            int(income_ok), int(marks_ok), int(course_ok), int(year_ok),
            name_score / 100, dob_score / 100, income_score / 100, bank_score / 100,
            overall_match / 100, int(duplicate_flag)
        ]])
        try:
            proba = model.predict_proba(features)[0]
            classes = model.classes_
            best_idx = np.argmax(proba)
            status = classes[best_idx]
            confidence = round(float(proba[best_idx]) * 100, 1)
            return status, confidence, flags
        except Exception:
            pass

    # Rule-based fallback
    return _rule_based_classify(eligible, overall_match, duplicate_flag, flags, match_scores)


def _rule_based_classify(eligible, overall_match, duplicate_flag, flags, match_scores):
    """Deterministic classification when ML model isn't available."""
    name_s = match_scores.get('name_match', 80)
    income_s = match_scores.get('income_match', 80)

    if duplicate_flag:
        return 'Suspicious', 15.0, flags

    if not eligible:
        confidence = max(5.0, round(overall_match * 0.3, 1))
        return 'Rejected', confidence, flags

    critical_mismatch = name_s < 60 or income_s < 50
    if critical_mismatch:
        return 'Suspicious', round(overall_match * 0.4, 1), flags

    has_flags = len(flags) > 0
    if has_flags or overall_match < 75:
        return 'Needs Review', round(overall_match * 0.75, 1), flags

    confidence = round(min(98, overall_match * 0.95 + 5), 1)
    return 'Approved', confidence, flags


def _load_model():
    """Load pre-trained model if available."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    return None


def train_model(X, y):
    """Train and save a Random Forest classifier."""
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    os.makedirs('models', exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    return model
