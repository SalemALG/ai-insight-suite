from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd


def score_churn(df: pd.DataFrame) -> List[Dict[str, Any]]:
	# Simple RFM-based heuristic scorer for demo purposes
	if "customer_id" not in df.columns:
		raise ValueError("customer_id column required for churn scoring")
	date_col = next((c for c in df.columns if c.lower() in ("date", "txn_date")), None)
	amount_col = next((c for c in df.columns if c.lower() in ("amount", "revenue", "value")), None)
	if not date_col or not amount_col:
		raise ValueError("need date and amount columns")
	data = df.copy()
	data[date_col] = pd.to_datetime(data[date_col])
	ref_date = data[date_col].max() + pd.Timedelta(days=1)
	grp = data.groupby("customer_id").agg(
		recency=(date_col, lambda s: (ref_date - s.max()).days),
		frequency=(date_col, "count"),
		monetary=(amount_col, "sum"),
	).reset_index()

	# Normalize
	for col in ("recency", "frequency", "monetary"):
		grp[col] = (grp[col] - grp[col].min()) / (grp[col].max() - grp[col].min() + 1e-6)
	# Higher recency means more days since last purchase → higher churn risk
	grp["churn_score"] = (grp["recency"] * 0.5) + ((1 - grp["frequency"]) * 0.25) + ((1 - grp["monetary"]) * 0.25)
	grp["bucket"] = pd.cut(grp["churn_score"], bins=[-0.01, 0.33, 0.66, 1.0], labels=["low", "medium", "high"]).astype(str)
	return grp[["customer_id", "churn_score", "bucket"]].to_dict(orient="records")


