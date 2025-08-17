from __future__ import annotations

import re
from typing import Iterable, List, Optional

from pydantic import BaseModel
from rapidfuzz import fuzz

from ai_insight_suite.libs.common.i18n import parse_arabic_numerals


PHONE_RE = re.compile(r"\b\+?\d[\d\s\-]{7,}\b")
EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}")
DATE_RE = re.compile(r"\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\b")
CURRENCY_RE = re.compile(r"\b(USD|EUR|SAR|AED|EGP|QAR|KWD|OMR|GBP)\b", re.I)
AMOUNT_RE = re.compile(r"\b\d{1,3}(?:[\,\s]\d{3})*(?:\.\d{1,2})?\b")
TOTAL_LABELS = ["total", "amount", "grand total", "vat", "tax", "الاجمالي", "المجموع", "المبلغ"]


class Field(BaseModel):
	key: str
	val: str | None
	confidence: float
	source_page: int | None = None


def _score(label: str, text: str) -> float:
	return fuzz.partial_ratio(label.lower(), text.lower()) / 100.0


def extract_fields(text: str, schema_yaml: Optional[str] = None, locale: str = "en") -> List[Field]:
	plain = parse_arabic_numerals(text)
	fields: List[Field] = []

	phones = PHONE_RE.findall(plain)
	if phones:
		fields.append(Field(key="phone", val=phones[0], confidence=0.8))

	emails = EMAIL_RE.findall(plain)
	if emails:
		fields.append(Field(key="email", val=emails[0], confidence=0.9))

	dates = DATE_RE.findall(plain)
	if dates:
		fields.append(Field(key="date", val=dates[0], confidence=0.7))

	currency = CURRENCY_RE.search(plain)
	if currency:
		fields.append(Field(key="currency", val=currency.group(1), confidence=0.75))

	amounts = AMOUNT_RE.findall(plain)
	if amounts:
		fields.append(Field(key="amount", val=amounts[-1], confidence=0.6))

	# total via fuzzy label search
	best = (None, 0.0)
	for lab in TOTAL_LABELS:
		s = _score(lab, plain)
		if s > best[1]:
			best = (lab, s)
	if best[0] and amounts:
		fields.append(Field(key="total", val=amounts[-1], confidence=min(1.0, 0.5 + best[1] / 2)))

	# TODO: support custom schema via YAML (regex pairs)
	return fields


