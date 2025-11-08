"""
Pytest Konfiguration und Fixtures
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import timedelta
from app.auth import create_access_token


@pytest.fixture
def client():
    """FastAPI Test Client"""
    return TestClient(app)


@pytest.fixture
def valid_token():
    """Gültiger JWT Token für Tests"""
    access_token_expires = timedelta(minutes=30)
    token = create_access_token(
        data={"sub": "test_user@example.com"},
        expires_delta=access_token_expires
    )
    return token


@pytest.fixture
def auth_headers(valid_token):
    """Authorization Headers für authentifizierte Requests"""
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.fixture
def sample_reservation():
    """Sample Reservierungsdaten für Tests"""
    from datetime import datetime, timezone
    return {
        "customer_name": "Test User",
        "customer_email": "test@example.com",
        "reservation_date": datetime(2025, 12, 24, 18, 0, 0, tzinfo=timezone.utc).isoformat(),
        "party_size": 4,
        "special_requests": "Vegetarisches Menü"
    }
