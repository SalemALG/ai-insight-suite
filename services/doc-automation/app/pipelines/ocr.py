from __future__ import annotations

import pathlib
from typing import Dict, Tuple

import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path


def _preprocess(image):
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	blur = cv2.medianBlur(gray, 3)
	thr = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
	return thr


def _image_from_file(path: pathlib.Path) -> list:
	ext = path.suffix.lower()
	if ext in [".pdf"]:
		pages = convert_from_path(str(path))
		return [cv2.cvtColor(np.array(p), cv2.COLOR_RGB2BGR) for p in pages]
	img = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)
	return [img]


def ocr_document(path: pathlib.Path, use_cloud: bool = False) -> Tuple[str, Dict]:
	# Local OCR via pytesseract; cloud backends are TODO hooks
	pages = _image_from_file(path)
	texts = []
	for idx, page in enumerate(pages, start=1):
		proc = _preprocess(page)
		config = "-l ara+eng --oem 3 --psm 6"
		text = pytesseract.image_to_string(proc, config=config)
		texts.append(text)
	return "\n".join(texts), {"pages": len(pages)}


