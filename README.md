## AI Insight Suite

Two-service mono-repo for a 2-person agency to deliver document automation (OCR+NLP) and predictive dashboards in one week. Designed to be industry-agnostic and bilingual-friendly (Arabic + English), containerized, and testable.

### Services
- **doc-automation**: Upload PDFs/images → OCR → extract structured fields → JSON/CSV export → optional Google Sheets sync. FastAPI API + Streamlit demo.
- **predictive**: Upload time-series data → forecasts and optional churn scoring → Streamlit dashboard + REST read endpoints.

### Quickstart (Docker Compose)
1. Copy env and adjust as needed:
   ```bash
   cp .env.example .env
   ```
2. Build and run all services:
   ```bash
   docker compose -f infra/docker-compose.yml up --build
   ```
3. Open:
   - Doc Automation API: `http://localhost:8001/docs`
   - Doc Automation Streamlit: `http://localhost:8501`
   - Predictive API: `http://localhost:8002/docs`
   - Predictive Streamlit: `http://localhost:8502`

### Local Dev
```bash
make install   # setup pre-commit hooks locally
make dev       # create venv and install deps for both services
make lint      # run black/isort/flake8/mypy
make test      # pytest for both services
```

### Layout
```
ai-insight-suite/
  libs/common/           # logging, config, i18n, storage, sheets client
  services/doc-automation
  services/predictive
  infra/docker-compose.yml
  .github/workflows/ci.yml
  Makefile
  .env.example
```

### Features & Standards
- Python 3.11, FastAPI (+ Pydantic v2), Streamlit
- OCR: pytesseract (local), optional AWS Textract / Google Vision via flags
- NLP: rules-based extractors with optional spaCy NER hook
- Forecasting: Prophet (if available) or SARIMAX fallback; XGBoost/LightGBM for churn
- Jobs: APScheduler
- Data: pandas, SQLAlchemy (SQLite; Postgres profile TBD)
- Auth: simple API key for admin routes
- DevX: pre-commit (black/isort/flake8/mypy)
- CI: GitHub Actions (lint + tests)
- Logging: JSON logs with request IDs
- i18n: Arabic/English helpers

### Security & Limits
- File size limits and allowed mimetypes enforced at upload
- CORS configuration
- Basic PDF safety checks (no embedded JS)

### Examples
- Doc Automation examples are referenced under `services/doc-automation/examples/`
- Predictive examples are under `services/predictive/examples/`

Note: Example binary images are not embedded here to keep repo lightweight; sample placeholders and download instructions are included. Tests mock OCR to avoid system dependencies.

### Make Targets
```bash
make up     # docker compose up
make down   # docker compose down -v
make clean  # remove build artifacts
```

### Roadmap / TODOs
- Postgres profile + migrations, multi-tenant auth, robust cloud OCR adapters, GPU inference paths.
- Expand NER to spaCy pipelines and Transformer models behind feature flags.
- Model registry and experiment tracking.


