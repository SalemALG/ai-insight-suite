from __future__ import annotations

import os
import pathlib
from datetime import datetime
from typing import Tuple

from slugify import slugify

BASE_DIR = pathlib.Path(__file__).resolve().parents[2] / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"
METRICS_DIR = BASE_DIR / "metrics"


for d in (UPLOADS_DIR, OUTPUTS_DIR, METRICS_DIR):
	d.mkdir(parents=True, exist_ok=True)


def safe_filename(name: str) -> str:
	return slugify(name, lowercase=False, separator="-")


def save_upload(content: bytes, original_name: str) -> pathlib.Path:
	stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
	filename = f"{stamp}-{safe_filename(original_name)}"
	path = UPLOADS_DIR / filename
	path.write_bytes(content)
	return path


def output_path(stem: str, ext: str) -> pathlib.Path:
	return OUTPUTS_DIR / f"{safe_filename(stem)}.{ext}"


