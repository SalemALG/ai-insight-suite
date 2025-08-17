from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from ai_insight_suite.libs.common.storage import output_path, save_upload
from ai_insight_suite.services.doc_automation.app.pipelines.ocr import ocr_document
from ai_insight_suite.services.doc_automation.app.pipelines.extract import extract_fields


st.set_page_config(page_title="Doc Automation", layout="wide")

st.title("Document Automation")
locale = st.selectbox("Locale", ["en", "ar"], index=0)
use_cloud = st.checkbox("Use Cloud OCR (if configured)", value=False)

uploaded = st.file_uploader("Upload PDF/Image", type=["pdf", "png", "jpg", "jpeg"])
if uploaded:
	content = uploaded.read()
	path = save_upload(content, uploaded.name)
	text, meta = ocr_document(path, use_cloud=use_cloud)
	fields = extract_fields(text, locale=locale)

	st.subheader("Extracted Text")
	st.text_area("text", text, height=200)

	rows = [{"key": f.key, "val": f.val, "confidence": f.confidence} for f in fields]
	df = pd.DataFrame(rows)
	st.subheader("Fields")
	st.dataframe(df)

	csv_p = output_path(path.stem + "-extracted", "csv")
	json_p = output_path(path.stem + "-extracted", "json")
	df.to_csv(csv_p, index=False)
	json_p.write_text(json.dumps({"text": text, "fields": rows}, ensure_ascii=False))

	st.download_button("Download CSV", data=df.to_csv(index=False), file_name=csv_p.name)
	st.download_button("Download JSON", data=json.dumps({"text": text, "fields": rows}, ensure_ascii=False), file_name=json_p.name)
