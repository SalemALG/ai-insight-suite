from __future__ import annotations

import io

import pandas as pd
import plotly.express as px
import streamlit as st

from ai_insight_suite.services.predictive.app.pipelines.forecast import forecast_dataframe
from ai_insight_suite.services.predictive.app.pipelines.churn import score_churn


st.set_page_config(page_title="Predictive Dashboard", layout="wide")

st.title("Predictive Dashboard")
tab_overview, tab_forecast, tab_churn = st.tabs(["Overview", "Forecast", "Churn"])

with tab_forecast:
	st.subheader("Upload Time Series")
	file = st.file_uploader("CSV/XLSX", type=["csv", "xlsx"], key="ts")
	horizon = st.slider("Horizon (periods)", 4, 52, 12)
	freq = st.selectbox("Frequency", ["D", "W", "M"], index=1)
	if file:
		data = file.read()
		df = pd.read_csv(io.BytesIO(data)) if file.name.endswith(".csv") else pd.read_excel(io.BytesIO(data))
		res = forecast_dataframe(df, horizon=horizon, freq=freq)
		pred_df = pd.DataFrame(res["predictions"]).rename(columns={"ds": "date"})
		fig = px.line(pred_df, x="date", y=["yhat", "yhat_lower", "yhat_upper"], title="Forecast")
		st.plotly_chart(fig, use_container_width=True)
		st.json(res["metrics"]) 

with tab_churn:
	st.subheader("Upload Transactions")
	file2 = st.file_uploader("CSV/XLSX", type=["csv", "xlsx"], key="churn")
	if file2:
		data2 = file2.read()
		df2 = pd.read_csv(io.BytesIO(data2)) if file2.name.endswith(".csv") else pd.read_excel(io.BytesIO(data2))
		results = score_churn(df2)
		st.dataframe(pd.DataFrame(results))
