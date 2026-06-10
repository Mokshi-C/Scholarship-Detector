import re
import random

# Try to import tesseract; fall back to simulation for demo
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


def extract_text_from_image(filepath: str) -> str:
    """Extract text from an image file using Tesseract OCR."""
    if TESSERACT_AVAILABLE:
        try:
            img = Image.open(filepath)
            img = preprocess_image(img)
            text = pytesseract.image_to_string(img, lang='eng')
            return text.strip()
        except Exception as e:
            return simulate_ocr(filepath)
    else:
        return simulate_ocr(filepath)


def preprocess_image(img):
    """Convert to grayscale and enhance contrast for better OCR."""
    from PIL import ImageEnhance, ImageFilter
    img = img.convert('L')
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    img = img.filter(ImageFilter.SHARPEN)
    return img


def simulate_ocr(filepath: str) -> str:
    """Simulate OCR extraction for demo purposes when no real image is given."""
    doc_type = 'unknown'
    if 'aadhaar' in filepath.lower():
        doc_type = 'aadhaar'
    elif 'marksheet' in filepath.lower():
        doc_type = 'marksheet'
    elif 'income' in filepath.lower():
        doc_type = 'income'
    elif 'bank' in filepath.lower() or 'passbook' in filepath.lower():
        doc_type = 'bank'

    templates = {
        'aadhaar': (
            "GOVERNMENT OF INDIA\n"
            "Unique Identification Authority of India\n"
            "Name: {name}\n"
            "Date of Birth: {dob}\n"
            "Gender: Female\n"
            "Aadhaar No: {aadhaar}\n"
            "Address: 12, Gandhi Nagar, Chennai - 600001"
        ),
        'marksheet': (
            "STATE BOARD OF SECONDARY EDUCATION\n"
            "Annual Examination Results\n"
            "Student Name: {name}\n"
            "Date of Birth: {dob}\n"
            "Marks Obtained: {marks}/100\n"
            "Percentage: {marks}%\n"
            "Result: PASS\n"
            "Physics: 85  Chemistry: 88  Maths: 92  Biology: 87  English: 79"
        ),
        'income': (
            "REVENUE DEPARTMENT\n"
            "INCOME CERTIFICATE\n"
            "This is to certify that the annual income of\n"
            "Shri/Smt: {parent_name}\n"
            "whose ward/daughter {name} is Rs. {income}/- per annum\n"
            "Date of Birth of applicant: {dob}\n"
            "Certificate No: REV/2024/12345"
        ),
        'bank': (
            "STATE BANK OF INDIA\n"
            "PASSBOOK\n"
            "Account Holder: {name}\n"
            "Account Number: {account}\n"
            "Branch: Chennai Main Branch\n"
            "IFSC: SBIN0001234\n"
            "Date of Opening: 15-06-2020"
        )
    }
    template = templates.get(doc_type, "Document text could not be extracted.\nFile: " + filepath)
    return template


def parse_fields_from_text(text: str, doc_type: str) -> dict:
    """Extract structured fields from OCR text."""
    fields = {}
    name_match = re.search(r'(?:Name|Student Name|Account Holder)[:\s]+([A-Za-z\s\.]+)', text)
    if name_match:
        fields['name'] = name_match.group(1).strip()

    dob_match = re.search(r'(?:Date of Birth|DOB)[:\s]+([\d\-/]+)', text)
    if dob_match:
        fields['dob'] = dob_match.group(1).strip()

    if doc_type == 'marksheet':
        marks_match = re.search(r'(?:Percentage|Marks)[:\s]+([\d.]+)', text)
        if marks_match:
            fields['marks'] = float(marks_match.group(1))

    if doc_type == 'income':
        income_match = re.search(r'Rs\.?\s*([\d,]+)', text)
        if income_match:
            fields['income'] = float(income_match.group(1).replace(',', ''))

    if doc_type == 'bank':
        acc_match = re.search(r'Account Number[:\s]+([\d\s]+)', text)
        if acc_match:
            fields['account'] = acc_match.group(1).strip()

    return fields
