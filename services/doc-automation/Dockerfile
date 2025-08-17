FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY services/doc-automation/requirements.txt /tmp/req.txt
RUN pip install --no-cache-dir -r /tmp/req.txt

COPY . /app
ENV PYTHONPATH=/app

CMD ["uvicorn", "ai_insight_suite.services.doc_automation.app.main:app", "--host", "0.0.0.0", "--port", "8000"]


