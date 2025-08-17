from __future__ import annotations

from typing import Any, Dict, List, Optional

import gspread
from google.oauth2.service_account import Credentials

from .config import settings


def _get_client() -> Optional[gspread.Client]:
	creds_json = settings.GOOGLE_SHEETS_CREDS_JSON
	if not creds_json:
		return None
	scopes = [
		"https://www.googleapis.com/auth/spreadsheets",
		"https://www.googleapis.com/auth/drive.file",
	]
	creds = Credentials.from_service_account_info(
		_ensure_json(creds_json), scopes=scopes
	)
	return gspread.authorize(creds)


def _ensure_json(text_or_json: Any) -> Dict[str, Any]:
	if isinstance(text_or_json, dict):
		return text_or_json
	import json

	return json.loads(text_or_json)


def append_row(sheet_id: str, worksheet: str, row: List[Any]) -> bool:
	client = _get_client()
	if not client:
		return False
	sh = client.open_by_key(sheet_id)
	ws = sh.worksheet(worksheet)
	ws.append_row(row)
	return True


def upsert_by_key(sheet_id: str, worksheet: str, key_col: str, key_val: str, data: Dict[str, Any]) -> bool:
	client = _get_client()
	if not client:
		return False
	sh = client.open_by_key(sheet_id)
	ws = sh.worksheet(worksheet)
	headers = ws.row_values(1)
	key_idx = headers.index(key_col) + 1
	cell = ws.find(key_val, in_column=key_idx)
	if cell:
		row_idx = cell.row
	else:
		row_idx = ws.row_count + 1
		ws.add_rows(1)
	for col_name, value in data.items():
		if col_name not in headers:
			headers.append(col_name)
			ws.update_cell(1, len(headers), col_name)
		col_idx = headers.index(col_name) + 1
		ws.update_cell(row_idx, col_idx, value)
	return True


