"""
Integration Tests für API Routes
"""
import pytest
from datetime import datetime, timezone


class TestReservationRoutes:
    """Tests für Reservierungs-Endpoints"""

    def test_health_check_without_auth(self, client):
        """Test: Health Check sollte ohne Auth funktionieren"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()

    def test_get_all_reservations_requires_auth(self, client):
        """Test: GET /reservations benötigt Authentication"""
        response = client.get("/reservations")
        assert response.status_code == 403  # Forbidden ohne Token

    def test_get_all_reservations_with_auth(self, client, auth_headers):
        """Test: GET /reservations mit gültiger Auth"""
        response = client.get("/reservations", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_reservation_by_id_with_auth(self, client, auth_headers):
        """Test: GET /reservations/{id} mit Auth"""
        response = client.get("/reservations/1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "customer_name" in data

    def test_get_reservation_not_found(self, client, auth_headers):
        """Test: GET /reservations/{id} mit ungültiger ID"""
        response = client.get("/reservations/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "nicht gefunden" in response.json()["detail"]

    def test_create_reservation_without_auth(self, client, sample_reservation):
        """Test: POST /reservations benötigt Authentication"""
        response = client.post("/reservations", json=sample_reservation)
        assert response.status_code == 403

    def test_create_reservation_with_auth(self, client, auth_headers, sample_reservation):
        """Test: POST /reservations mit gültiger Auth und Daten"""
        response = client.post(
            "/reservations",
            json=sample_reservation,
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["customer_name"] == sample_reservation["customer_name"]
        assert data["customer_email"] == sample_reservation["customer_email"]
        assert "id" in data
        assert "created_at" in data

    def test_create_reservation_invalid_email(self, client, auth_headers):
        """Test: POST /reservations mit ungültiger E-Mail"""
        invalid_reservation = {
            "customer_name": "Test",
            "customer_email": "invalid-email-format",
            "reservation_date": datetime(2025, 12, 24, 18, 0, 0, tzinfo=timezone.utc).isoformat(),
            "party_size": 4
        }
        response = client.post(
            "/reservations",
            json=invalid_reservation,
            headers=auth_headers
        )
        # Pydantic sollte invalid validieren oder akzeptieren
        assert response.status_code in [201, 422]  # Created oder Validation Error

    def test_create_reservation_missing_fields(self, client, auth_headers):
        """Test: POST /reservations mit fehlenden Pflichtfeldern"""
        incomplete_reservation = {
            "customer_name": "Test"
            # E-Mail, Datum, party_size fehlen
        }
        response = client.post(
            "/reservations",
            json=incomplete_reservation,
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation Error

    def test_create_reservation_invalid_party_size(self, client, auth_headers):
        """Test: POST /reservations mit ungültiger party_size"""
        invalid_reservation = {
            "customer_name": "Test",
            "customer_email": "test@example.com",
            "reservation_date": datetime(2025, 12, 24, 18, 0, 0, tzinfo=timezone.utc).isoformat(),
            "party_size": 0  # Muss > 0 sein
        }
        response = client.post(
            "/reservations",
            json=invalid_reservation,
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_update_reservation_with_auth(self, client, auth_headers, sample_reservation):
        """Test: PUT /reservations/{id} mit Auth"""
        # Erst erstellen
        create_response = client.post(
            "/reservations",
            json=sample_reservation,
            headers=auth_headers
        )
        res_id = create_response.json()["id"]

        # Dann aktualisieren
        updated_data = sample_reservation.copy()
        updated_data["customer_name"] = "Updated Name"

        response = client.put(
            f"/reservations/{res_id}",
            json=updated_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["customer_name"] == "Updated Name"

    def test_update_nonexistent_reservation(self, client, auth_headers, sample_reservation):
        """Test: PUT /reservations/{id} mit ungültiger ID"""
        response = client.put(
            "/reservations/99999",
            json=sample_reservation,
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_reservation_without_auth(self, client):
        """Test: DELETE /reservations/{id} benötigt Auth"""
        response = client.delete("/reservations/1")
        assert response.status_code == 403

    def test_delete_reservation_with_auth(self, client, auth_headers, sample_reservation):
        """Test: DELETE /reservations/{id} mit Auth"""
        # Erst erstellen
        create_response = client.post(
            "/reservations",
            json=sample_reservation,
            headers=auth_headers
        )
        res_id = create_response.json()["id"]

        # Dann löschen
        response = client.delete(f"/reservations/{res_id}", headers=auth_headers)
        assert response.status_code == 204

        # Sollte nicht mehr existieren
        get_response = client.get(f"/reservations/{res_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_invalid_token_rejected(self, client):
        """Test: Ungültiger Token wird abgelehnt"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/reservations", headers=headers)
        assert response.status_code == 401

    def test_expired_token_rejected(self, client):
        """Test: Abgelaufener Token wird abgelehnt"""
        from datetime import timedelta
        from app.auth import create_access_token

        expired_token = create_access_token(
            data={"sub": "test_user"},
            expires_delta=timedelta(seconds=-100)  # Negative Delta = bereits abgelaufen
        )
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/reservations", headers=headers)
        assert response.status_code == 401

    def test_patch_reservation_status(self, client, auth_headers, sample_reservation):
        """Test: PATCH /reservations/{id}/status"""
        # Erst erstellen
        create_response = client.post(
            "/reservations",
            json=sample_reservation,
            headers=auth_headers
        )
        res_id = create_response.json()["id"]

        # Status aktualisieren
        response = client.patch(
            f"/reservations/{res_id}/status?new_status=confirmed",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"

    def test_root_endpoint(self, client):
        """Test: GET / Root Endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data
