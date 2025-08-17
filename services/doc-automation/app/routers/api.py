from __future__ import annotations

import io
import json
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from ai_insight_suite.libs.common.config import settings
from ai_insight_suite.libs.common.logging import get_logger
from ai_insight_suite.libs.common.storage import output_path, save_upload
from ..pipelines.ocr import ocr_document
from ..pipelines.extract import extract_fields


router = APIRouter()
log = get_logger("doc.api")


class FieldResult(BaseModel):
	key: str
	val: str | None
	confidence: float
	source_page: int | None = None


class ExtractResponse(BaseModel):
	text: str
	fields: List[FieldResult]
	summary: Dict[str, Any]
	csv_path: Optional[str]
	json_path: Optional[str]


def _require_admin(key: str = Form(...)):
	if not settings.ADMIN_API_KEY or key != settings.ADMIN_API_KEY:
		raise HTTPException(status_code=401, detail="invalid api key")


@router.post("/extract", response_model=ExtractResponse)
async def extract(
	file: UploadFile = File(...),
	schema_yaml: Optional[str] = Form(None),
	use_cloud: bool = Form(False),
	push_to_sheets: bool = Form(False),
	sheet_id: Optional[str] = Form(None),
):
	content = await file.read()
	path = save_upload(content, file.filename)
	text, ocr_meta = ocr_document(path, use_cloud=use_cloud)
	fields = extract_fields(text, schema_yaml=schema_yaml, locale=settings.DEFAULT_LOCALE)

	rows = [{"key": f.key, "val": f.val, "confidence": f.confidence} for f in fields]
	df = pd.DataFrame(rows)
	csv_p = output_path(path.stem + "-extracted", "csv")
	json_p = output_path(path.stem + "-extracted", "json")
	df.to_csv(csv_p, index=False)
	json_p.write_text(json.dumps({"text": text, "fields": rows}, ensure_ascii=False))

	# Sheets push is a no-op unless creds provided (handled inside client)
	if push_to_sheets and sheet_id:
		try:
			from ai_insight_suite.libs.common.sheets import append_row

			append_row(sheet_id, "Sheet1", [file.filename] + [r.get("val") for r in rows])
		except Exception as e:  # noqa: BLE001
			log.warning("sheets_push_failed", error=str(e))

	return ExtractResponse(
		text=text,
		fields=fields,
		summary={"pages": ocr_meta.get("pages", 1)},
		csv_path=str(csv_p),
		json_path=str(json_p),
	)


class AdminValidateBody(BaseModel):
	key: str
	file_name: str
	corrected_json: Dict[str, Any]


@router.post("/admin/validate")
async def admin_validate(body: AdminValidateBody, _: Any = Depends(_require_admin)):
	json_p = output_path(body.file_name + "-corrected", "json")
	json_p.write_text(json.dumps(body.corrected_json, ensure_ascii=False))
	return {"ok": True, "path": str(json_p)}


