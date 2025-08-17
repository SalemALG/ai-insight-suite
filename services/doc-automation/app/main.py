from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai_insight_suite.libs.common.logging import RequestIdMiddleware, configure_logging
from .routers import api


configure_logging()
app = FastAPI(title="AI Insight Suite - Doc Automation", version="0.1.0")

app.add_middleware(RequestIdMiddleware)
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.get("/healthz")
async def healthz():
	return {"status": "ok"}


app.include_router(api.router, prefix="/v1")


