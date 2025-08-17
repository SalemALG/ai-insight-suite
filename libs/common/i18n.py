from __future__ import annotations

import datetime as dt
from babel.dates import format_date, format_datetime
from babel.numbers import format_currency, format_decimal, parse_decimal

AR_DIGITS = {
	"0": "٠",
	"1": "١",
	"2": "٢",
	"3": "٣",
	"4": "٤",
	"5": "٥",
	"6": "٦",
	"7": "٧",
	"8": "٨",
	"9": "٩",
}


def to_locale_number(value: float | int | str, locale: str = "en") -> str:
	if isinstance(value, (int, float)):
		text = format_decimal(value, locale=locale)
	else:
		text = value
	if locale.startswith("ar"):
		return "".join(AR_DIGITS.get(ch, ch) for ch in str(text))
	return str(text)


def to_locale_date(value: dt.date | dt.datetime, locale: str = "en") -> str:
	if isinstance(value, dt.datetime):
		return format_datetime(value, locale=locale)
	return format_date(value, locale=locale)


def format_money(amount: float, currency_code: str = "USD", locale: str = "en") -> str:
	return format_currency(amount, currency_code, locale=locale)


def is_rtl(locale: str) -> bool:
	return locale.startswith("ar")


def parse_arabic_numerals(text: str) -> str:
	rev = {v: k for k, v in AR_DIGITS.items()}
	return "".join(rev.get(ch, ch) for ch in text)


