from app.core.config import settings


def test_settings_loaded():
    """Verify that configuration settings load expected defaults."""
    assert settings.ORBIT_APP_NAME == "ORBIT Geospatial Intelligence"
    assert settings.ORBIT_API_V1_STR == "/api/v1"
    assert settings.ORBIT_HOST == "127.0.0.1"
    assert settings.ORBIT_PORT == 8000
    assert "http://localhost:5173" in settings.ORBIT_CORS_ORIGINS
