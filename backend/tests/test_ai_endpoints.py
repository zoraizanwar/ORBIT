from unittest.mock import AsyncMock, MagicMock
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import get_db


@pytest.fixture
def mock_db_session():
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    async def _override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = _override_get_db
    yield mock_session
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_ai_package_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "aoi_id": "aoi-sinop-mato-grosso",
            "aoi_name": "Sinop Deforestation Frontier",
        }
        resp = await client.post("/api/v1/ai/evidence/package", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "package_id" in data
        assert "evidence_items" in data
        assert len(data["evidence_items"]) >= 5
        assert len(data["package_hash_sha256"]) == 64


@pytest.mark.asyncio
async def test_ai_interpret_endpoint(mock_db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "aoi_id": "aoi-sinop-mato-grosso",
            "interpretation_type": "URBAN_EXPANSION_SYNTHESIS",
            "user_prompt": "Synthesize canopy deficit and road corridor clearings",
        }
        resp = await client.post("/api/v1/ai/interpret", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["epistemic_level"] == "AI_INTERPRETED"
        assert len(data["claims"]) >= 3
        assert len(data["recommendations"]) >= 1


@pytest.mark.asyncio
async def test_ai_claims_validate_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First get package
        pkg_resp = await client.post("/api/v1/ai/evidence/package", json={"aoi_id": "aoi-sinop-mato-grosso"})
        pkg_data = pkg_resp.json()

        payload = {
            "evidence_package": pkg_data,
            "claims": [
                {
                    "claim_id": "c-valid",
                    "claim_text": "Canopy deficit of -0.24 is confirmed.",
                    "claim_type": "CHANGE",
                    "evidence_ids": ["ev-ndvi-delta"],
                    "epistemic_level": "AI_INTERPRETED",
                }
            ],
        }
        resp = await client.post("/api/v1/ai/claims/validate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_all_valid"] is True
        assert data["claims_count"] == 1


@pytest.mark.asyncio
async def test_ai_report_generate_endpoint(mock_db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "aoi_id": "aoi-sinop-mato-grosso",
            "title": "Sinop Comprehensive Grounded Intelligence Report",
            "report_format": "MARKDOWN",
        }
        resp = await client.post("/api/v1/ai/reports/generate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "report_id" in data
        assert "# ORBIT GEOSPATIAL INTELLIGENCE REPORT" in data["content_text"]
        assert len(data["provenance_hash_sha256"]) == 64


@pytest.mark.asyncio
async def test_ai_decision_support_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "aoi_id": "aoi-sinop-mato-grosso",
        }
        resp = await client.post("/api/v1/ai/decision-support", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) >= 1


def test_alembic_migration_0008_script_validity():
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    rev = script.get_revision("0008_grounded_ai_intelligence")
    assert rev is not None
    assert rev.down_revision == "0007_forecasting_foundation"
