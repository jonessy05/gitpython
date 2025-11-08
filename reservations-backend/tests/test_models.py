"""
Unit Tests für Pydantic Models
"""
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
from app.models import (
    Reservation,
    ReservationCreate,
    ReservationStatus,
)


class TestReservationValidation:
    """Tests für Reservierungs-Model Validierung"""

    def test_valid_reservation_create(self):
        """Test: Gültige Reservierung kann erstellt werden"""
        data = {
            "customer_name": "Max Mustermann",
            "customer_email": "max@example.com",
            "reservation_date": datetime(2025, 12, 24, 18, 0, 0, tzinfo=timezone.utc),
            "party_size": 4,
            "special_requests": "Fensterplatz"
        }
        reservation = ReservationCreate(**data)
        assert reservation.customer_name == "Max Mustermann"
        assert reservation.customer_email == "max@example.com"
        assert reservation.party_size == 4

    def test_empty_customer_name_fails(self):
        """Test: Leerer customer_name wird abgelehnt"""
        data = {
            "customer_name": "",
            "customer_email": "max@example.com",
            "reservation_date": datetime(2025, 12, 24, 18, 0, 0, tzinfo=timezone.utc),
            "party_size": 4
        }
        with pytest.raises(ValidationError) as exc_info:
            ReservationCreate(**data)
        assert "at least 1 character" in str(exc_info.value)

    def test_invalid_party_size_zero(self):
        """Test: party_size muss > 0 sein"""
        data = {
            "customer_name": "Max",
            "customer_email": "max@example.com",
            "reservation_date": datetime(2025, 12, 24, 18, 0, 0, tzinfo=timezone.utc),
            "party_size": 0
        }
        with pytest.raises(ValidationError) as exc_info:
            ReservationCreate(**data)
        assert "greater than 0" in str(exc_info.value)

    def test_invalid_party_size_negative(self):
        """Test: party_size darf nicht negativ sein"""
        data = {
            "customer_name": "Max",
            "customer_email": "max@example.com",
            "reservation_date": datetime(2025, 12, 24, 18, 0, 0, tzinfo=timezone.utc),
            "party_size": -5
        }
        with pytest.raises(ValidationError):
            ReservationCreate(**data)

    def test_missing_required_fields(self):
        """Test: Pflichtfelder werden validiert"""
        data = {
            "customer_name": "Max",
            # customer_email fehlt
            "reservation_date": datetime(2025, 12, 24, 18, 0, 0, tzinfo=timezone.utc),
            "party_size": 4
        }
        with pytest.raises(ValidationError) as exc_info:
            ReservationCreate(**data)
        assert "customer_email" in str(exc_info.value)

    def test_optional_special_requests(self):
        """Test: special_requests ist optional"""
        data = {
            "customer_name": "Max",
            "customer_email": "max@example.com",
            "reservation_date": datetime(2025, 12, 24, 18, 0, 0, tzinfo=timezone.utc),
            "party_size": 4
            # special_requests ist optional
        }
        reservation = ReservationCreate(**data)
        assert reservation.special_requests is None

    def test_reservation_status_enum(self):
        """Test: ReservationStatus Enum funktioniert korrekt"""
        assert ReservationStatus.PENDING == "pending"
        assert ReservationStatus.CONFIRMED == "confirmed"
        assert ReservationStatus.CANCELLED == "cancelled"
        assert ReservationStatus.COMPLETED == "completed"

    def test_full_reservation_with_id(self):
        """Test: Vollständiges Reservation Model mit ID"""
        now = datetime.now(timezone.utc)
        data = {
            "id": 1,
            "customer_name": "Max",
            "customer_email": "max@example.com",
            "reservation_date": now,
            "party_size": 4,
            "special_requests": "Test",
            "status": ReservationStatus.CONFIRMED,
            "created_at": now,
            "updated_at": now
        }
        reservation = Reservation(**data)
        assert reservation.id == 1
        assert reservation.status == ReservationStatus.CONFIRMED
