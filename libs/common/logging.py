from __future__ import annotations

import logging
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Any, Callable, Dict

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def _add_request_id(_, __, event_dict):
	req_id = request_id_ctx.get()
	if req_id:
		event_dict["request_id"] = req_id
	return event_dict


def configure_logging(level: int = logging.INFO) -> None:
	shared_processors = [
		structlog.contextvars.merge_contextvars,
		_add_request_id,
		structlog.processors.TimeStamper(fmt="iso", utc=True),
		structlog.processors.add_log_level,
	]

	structlog.configure(
		processors=shared_processors
		+ [
			structlog.processors.dict_tracebacks,
			structlog.processors.JSONRenderer(),
		],
		logger_factory=structlog.stdlib.LoggerFactory(),
		cache_logger_on_first_use=True,
	)

	logging.basicConfig(
		format="%(message)s",
		stream=sys.stdout,
		level=level,
	)


class RequestIdMiddleware(BaseHTTPMiddleware):
	def __init__(self, app):
		super().__init__(app)
		self.logger = structlog.get_logger("http")

	async def dispatch(self, request: Request, call_next: Callable[..., Any]):
		start = time.perf_counter()
		req_id = request.headers.get("x-request-id", str(uuid.uuid4()))
		request_id_ctx.set(req_id)
		response = await call_next(request)
		duration_ms = (time.perf_counter() - start) * 1000.0
		self.logger.info(
			"request",
			method=request.method,
			path=request.url.path,
			status_code=response.status_code,
			duration_ms=round(duration_ms, 2),
		)
		response.headers["x-request-id"] = req_id
		return response


def get_logger(name: str = "app") -> structlog.stdlib.BoundLogger:
	return structlog.get_logger(name)


