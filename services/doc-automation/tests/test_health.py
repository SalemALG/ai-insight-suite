from fastapi.testclient import TestClient

from ai_insight_suite.services.doc_automation.app.main import app


def test_health():
	client = TestClient(app)
	r = client.get("/healthz")
	assert r.status_code == 200
	assert r.json()["status"] == "ok"


