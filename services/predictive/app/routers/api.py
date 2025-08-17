from __future__ import annotations

import io
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from ai_insight_suite.libs.common.logging import get_logger
from ..pipelines.forecast import forecast_dataframe
from ..pipelines.churn import score_churn


router = APIRouter()
log = get_logger("pred.api")


class ForecastResponse(BaseModel):
	predictions: List[Dict[str, Any]]
	metrics: Dict[str, float]
	model_info: Dict[str, Any]


@router.post("/forecast", response_model=ForecastResponse)
async def forecast(
	file: UploadFile = File(...),
	horizon: int = Form(8),
	freq: str = Form("W"),
	model: str = Form("prophet"),
):
	content = await file.read()
	df = pd.read_csv(io.BytesIO(content)) if file.filename.endswith(".csv") else pd.read_excel(io.BytesIO(content))
	out = forecast_dataframe(df, horizon=horizon, freq=freq, model=model)
	return ForecastResponse(**out)


class ChurnResponse(BaseModel):
	results: List[Dict[str, Any]]


@router.post("/churn", response_model=ChurnResponse)
async def churn(file: UploadFile = File(...)):
	content = await file.read()
	df = pd.read_csv(io.BytesIO(content)) if file.filename.endswith(".csv") else pd.read_excel(io.BytesIO(content))
	results = score_churn(df)
	return ChurnResponse(results=results)


