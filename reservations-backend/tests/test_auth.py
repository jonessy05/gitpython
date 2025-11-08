"""
Unit Tests für Authentication und JWT
"""
import pytest
from datetime import datetime, timedelta, timezone
from app.auth import create_access_token, verify_token
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app


class TestJWTTokens:
    """Tests für JWT Token Management"""

    def test_create_token_success(self):
        """Test: Token kann erfolgreich erstellt werden"""
        token = create_access_token(data={"sub": "test_user"})
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_subject(self):
        """Test: Token enthält das Subject (sub)"""
        from jose import jwt
        import os

        user_id = "test@example.com"
        token = create_access_token(data={"sub": user_id})

        # Decode Token (ohne Verifikation für diesen Test)
        SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        assert payload["sub"] == user_id

    def test_token_has_expiration(self):
        """Test: Token hat ein Ablaufdatum"""
        from jose import jwt
        import os

        token = create_access_token(data={"sub": "test_user"})

        SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        assert "exp" in payload
        assert payload["exp"] > datetime.now(timezone.utc).timestamp()

    def test_token_custom_expiration(self):
        """Test: Custom Ablaufzeit wird beachtet"""
        from jose import jwt
        import os

        custom_expires = timedelta(hours=2)
        token = create_access_token(
            data={"sub": "test_user"},
            expires_delta=custom_expires
        )

        SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        # Expiration sollte in 2 Stunden sein (±5 Minuten Toleranz)
        now = datetime.now(timezone.utc).timestamp()
        expected_exp = now + (2 * 60 * 60)
        assert abs(payload["exp"] - expected_exp) < 300  # 5 Minuten Toleranz

    def test_token_with_additional_claims(self):
        """Test: Token kann zusätzliche Claims enthalten"""
        from jose import jwt
        import os

        token = create_access_token(data={
            "sub": "test_user",
            "role": "admin",
            "email": "test@example.com"
        })

        SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        assert payload["sub"] == "test_user"
        assert payload["role"] == "admin"
        assert payload["email"] == "test@example.com"


class TestTokenVerification:
    """Tests für Token Verifikation"""

    def test_verify_valid_token(self):
        """Test: Gültiger Token wird akzeptiert"""
        client = TestClient(app)
        token = create_access_token(data={"sub": "test_user"})
        headers = {"Authorization": f"Bearer {token}"}

        # Nutze einen geschützten Endpoint zum Testen
        response = client.get("/reservations", headers=headers)
        # 200 OK oder 500 ist ok - Hauptsache, Token wird akzeptiert (nicht 401)
        assert response.status_code != 401

    def test_verify_missing_token(self):
        """Test: Fehlender Token wird abgelehnt"""
        client = TestClient(app)
        # Kein Authorization Header
        response = client.get("/reservations")
        assert response.status_code == 403  # Forbidden

    def test_verify_invalid_token_format(self):
        """Test: Ungültiges Token-Format wird abgelehnt"""
        client = TestClient(app)
        headers = {"Authorization": "Bearer invalid.format"}
        response = client.get("/reservations", headers=headers)
        assert response.status_code == 401

    def test_verify_missing_bearer_prefix(self):
        """Test: Token ohne 'Bearer' Prefix wird abgelehnt"""
        client = TestClient(app)
        token = create_access_token(data={"sub": "test_user"})
        headers = {"Authorization": f"token {token}"}  # Falscher Prefix
        response = client.get("/reservations", headers=headers)
        assert response.status_code == 403

    def test_verify_expired_token(self):
        """Test: Abgelaufener Token wird abgelehnt"""
        client = TestClient(app)
        # Token mit negativer Expiration (bereits abgelaufen)
        token = create_access_token(
            data={"sub": "test_user"},
            expires_delta=timedelta(seconds=-100)
        )
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/reservations", headers=headers)
        assert response.status_code == 401

    def test_verify_token_missing_subject(self):
        """Test: Token ohne Subject wird abgelehnt"""
        from jose import jwt
        import os

        SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        ALGORITHM = "HS256"

        # Manuell einen Token ohne 'sub' erstellen
        payload = {
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            "role": "admin"
            # 'sub' fehlt!
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        client = TestClient(app)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/reservations", headers=headers)
        assert response.status_code == 401

    def test_multiple_valid_tokens(self):
        """Test: Mehrere verschiedene Tokens funktionieren"""
        token1 = create_access_token(data={"sub": "user1"})
        token2 = create_access_token(data={"sub": "user2"})

        client = TestClient(app)

        headers1 = {"Authorization": f"Bearer {token1}"}
        response1 = client.get("/reservations", headers=headers1)
        assert response1.status_code != 401

        headers2 = {"Authorization": f"Bearer {token2}"}
        response2 = client.get("/reservations", headers=headers2)
        assert response2.status_code != 401
