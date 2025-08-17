from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

	# Core
	DEFAULT_LOCALE: str = Field(default="en")
	TZ: str = Field(default="UTC")

	# Auth
	ADMIN_API_KEY: str | None = Field(default=None)

	# Optional Cloud OCR
	USE_TEXTRACT: bool = Field(default=False)
	USE_GVISION: bool = Field(default=False)

	# Providers
	AWS_ACCESS_KEY_ID: str | None = None
	AWS_SECRET_ACCESS_KEY: str | None = None
	AWS_REGION: str | None = None

	GCP_PROJECT_ID: str | None = None
	GCP_SERVICE_ACCOUNT_JSON: str | None = None

	# Google Sheets
	GOOGLE_SHEETS_CREDS_JSON: str | None = None

	# OpenAI (optional)
	OPENAI_API_KEY: str | None = None

	# Predictive
	USE_PROPHET: bool = False

	# Database
	DATABASE_URL: str = Field(default="sqlite:///./data/app.db")


settings = Settings()


