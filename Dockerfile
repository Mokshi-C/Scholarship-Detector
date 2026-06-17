# Optional: use this Dockerfile on Render instead of the native Python
# runtime if you want REAL OCR (actual Tesseract binary) rather than the
# app's built-in simulated-OCR fallback.
#
# Render's native Python buildpack (used if you don't select Docker) does
# NOT install system packages like tesseract-ocr — only what's in
# requirements.txt. Without this Dockerfile, ocr_engine.py's existing
# try/except will detect the missing binary and silently fall back to
# simulate_ocr(), which is fine for a demo but won't read real uploaded
# document images.
#
# To use: in Render's dashboard, when creating the service, choose
# "Docker" as the runtime instead of "Python", and it will pick this file
# up automatically.

FROM python:3.11-slim

# Install the actual Tesseract OCR engine + English language data at the OS level
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render sets $PORT at runtime; gunicorn binds to it here
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
