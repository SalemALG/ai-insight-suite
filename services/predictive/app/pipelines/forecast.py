from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


def _prep(df: pd.DataFrame) -> pd.DataFrame:
	df = df.copy()
	date_col = next((c for c in df.columns if c.lower() in ("date", "ds")), None)
	metric_col = next((c for c in df.columns if c.lower() in ("metric", "y", "revenue", "count")), None)
	if not date_col or not metric_col:
		raise ValueError("input must contain 'date' and 'metric' (or 'revenue'/'count') columns")
	df[date_col] = pd.to_datetime(df[date_col])
	return df.rename(columns={date_col: "ds", metric_col: "y"}).sort_values("ds")


def forecast_dataframe(df: pd.DataFrame, horizon: int = 8, freq: str = "W", model: str = "sarimax") -> Dict[str, Any]:
	df = _prep(df)
	df = df.set_index("ds").asfreq(freq)
	df["y"] = df["y"].interpolate()

	# Minimal SARIMAX fallback that works everywhere; Prophet optional via settings
	order = (1, 1, 1)
	seasonal_order = (1, 1, 1, 12 if freq.upper().startswith("M") else 52 if freq.upper().startswith("W") else 7)
	model = SARIMAX(df["y"], order=order, seasonal_order=seasonal_order, enforce_stationarity=False, enforce_invertibility=False)
	res = model.fit(disp=False)
	fc = res.get_forecast(steps=horizon)
	pred = fc.predicted_mean
	ci = fc.conf_int(alpha=0.2)

	index = pd.date_range(start=df.index[-1], periods=horizon + 1, freq=freq)[1:]
	pred.index = index
	ci.index = index

	out_df = pd.DataFrame({
		"ds": index,
		"yhat": pred.values,
		"yhat_lower": ci.iloc[:, 0].values,
		"yhat_upper": ci.iloc[:, 1].values,
	})

	# naive metrics for demo
	last_hist = df["y"].tail(min(10, len(df)))
	mape = float(np.mean(np.abs((last_hist - last_hist.mean()) / (last_hist + 1e-6))) * 100)

	return {
		"predictions": out_df.to_dict(orient="records"),
		"metrics": {"mape": round(mape, 2)},
		"model_info": {"model": "sarimax", "order": order, "seasonal_order": seasonal_order},
	}


