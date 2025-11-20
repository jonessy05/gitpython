"""
Unit Tests für Pydantic Models
Testet Validierung, Default-Werte und Constraints
"""
import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4, UUID
from pydantic import ValidationError

from app.models import (
    ReservationBase,
    ReservationCreate,
    Reservation,
    ReservationStatus,
    DEFAULT_ROOM_ID
)


class TestReservationBase:
    """Unit Tests für ReservationBase Model"""

    def test_valid_reservation_base(self):
        """Test: Valides ReservationBase Model erstellen"""
        data = {
            "customer_name": "Max Mustermann",
            "customer_email": "max@example.com",
            "reservation_date": datetime.now(timezone.utc) + timedelta(days=1),
            "party_size": 4
        }
        reservation = ReservationBase(**data)
        
        assert reservation.customer_name == "Max Mustermann"
        assert reservation.customer_email == "max@example.com"
        assert reservation.party_size == 4
        assert reservation.room_id == DEFAULT_ROOM_ID

    def test_email_validation(self):
        """Test: Email Validierung schlägt bei ungültiger Email fehl"""
        data = {
            "customer_name": "Max Mustermann",
            "customer_email": "invalid-email",
            "reservation_date": datetime.now(timezone.utc) + timedelta(days=1),
            "party_size": 4
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ReservationBase(**data)
        
        assert "customer_email" in str(exc_info.value)

    def test_party_size_validation(self):
        """Test: party_size muss größer als 0 sein"""
        data = {
            "customer_name": "Max Mustermann",
            "customer_email": "max@example.com",
            "reservation_date": datetime.now(timezone.utc) + timedelta(days=1),
            "party_size": 0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ReservationBase(**data)
        
        assert "party_size" in str(exc_info.value)

    def test_party_size_exceeds_maximum(self):
        """Test: party_size darf 100 nicht überschreiten"""
        data = {
            "customer_name": "Max Mustermann",
            "customer_email": "max@example.com",
            "reservation_date": datetime.now(timezone.utc) + timedelta(days=1),
            "party_size": 101
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ReservationBase(**data)
        
        assert "party_size" in str(exc_info.value)

    def test_special_requests_optional(self):
        """Test: special_requests ist optional"""
        data = {
            "customer_name": "Max Mustermann",
            "customer_email": "max@example.com",
            "reservation_date": datetime.now(timezone.utc) + timedelta(days=1),
            "party_size": 4
        }
        reservation = ReservationBase(**data)
        
        assert reservation.special_requests is None

    def test_room_id_defaults_to_default(self):
        """Test: room_id verwendet DEFAULT_ROOM_ID wenn nicht gesetzt"""
        data = {
            "customer_name": "Max Mustermann",
            "customer_email": "max@example.com",
            "reservation_date": datetime.now(timezone.utc) + timedelta(days=1),
            "party_size": 4
        }
        reservation = ReservationBase(**data)
        
        assert reservation.room_id == DEFAULT_ROOM_ID

    def test_room_id_normalization_empty_string(self):
        """Test: Leere room_id wird auf DEFAULT_ROOM_ID normalisiert"""
        data = {
            "customer_name": "Max Mustermann",
            "customer_email": "max@example.com",
            "reservation_date": datetime.now(timezone.utc) + timedelta(days=1),
            "party_size": 4,
            "room_id": ""
        }
        reservation = ReservationBase(**data)
        
        assert reservation.room_id == DEFAULT_ROOM_ID

    def test_room_id_normalization_whitespace(self):
        """Test: Whitespace-only room_id wird auf DEFAULT_ROOM_ID normalisiert"""
        data = {
            "customer_name": "Max Mustermann",
            "customer_email": "max@example.com",
            "reservation_date": datetime.now(timezone.utc) + timedelta(days=1),
            "party_size": 4,
            "room_id": "   "
        }
        reservation = ReservationBase(**data)
        
        assert reservation.room_id == DEFAULT_ROOM_ID

    def test_room_id_normalization_none(self):
        """Test: None room_id wird auf DEFAULT_ROOM_ID normalisiert"""
        data = {
            "customer_name": "Max Mustermann",
            "customer_email": "max@example.com",
            "reservation_date": datetime.now(timezone.utc) + timedelta(days=1),
            "party_size": 4,
            "room_id": None
        }
        reservation = ReservationBase(**data)
        
        assert reservation.room_id == DEFAULT_ROOM_ID

    def test_room_id_custom_value(self):
        """Test: Benutzerdefinierte room_id wird beibehalten"""
        custom_room_id = "custom-room-123"
        data = {
            "customer_name": "Max Mustermann",
            "customer_email": "max@example.com",
            "reservation_date": datetime.now(timezone.utc) + timedelta(days=1),
            "party_size": 4,
            "room_id": custom_room_id
        }
        reservation = ReservationBase(**data)
        
        assert reservation.room_id == custom_room_id


class TestReservationCreate:
    """Unit Tests für ReservationCreate Model"""

    def test_valid_reservation_create(self):
        """Test: Valides ReservationCreate Model erstellen"""
        future_date = datetime.now(timezone.utc) + timedelta(days=7)
        data = {
            "customer_name": "Anna Schmidt",
            "customer_email": "anna@example.com",
            "reservation_date": future_date,
            "party_size": 2
        }
        reservation = ReservationCreate(**data)
        
        assert reservation.customer_name == "Anna Schmidt"
        assert reservation.reservation_date == future_date

    def test_reservation_date_in_past_fails(self):
        """Test: Reservierungsdatum in der Vergangenheit wird abgelehnt"""
        past_date = datetime.now(timezone.utc) - timedelta(days=1)
        data = {
            "customer_name": "Anna Schmidt",
            "customer_email": "anna@example.com",
            "reservation_date": past_date,
            "party_size": 2
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ReservationCreate(**data)
        
        assert "past" in str(exc_info.value).lower()


class TestReservation:
    """Unit Tests für vollständiges Reservation Model"""

    def test_valid_reservation(self):
        """Test: Vollständiges Reservation Model mit allen Feldern"""
        reservation_id = uuid4()
        now = datetime.now(timezone.utc)
        data = {
            "id": reservation_id,
            "customer_name": "Jonas",
            "customer_email": "jonas@example.com",
            "reservation_date": now + timedelta(days=5),
            "party_size": 6,
            "special_requests": "Fensterplatz",
            "room_id": "room-abc-123",
            "status": ReservationStatus.CONFIRMED,
            "created_at": now,
            "updated_at": now
        }
        reservation = Reservation(**data)
        
        assert reservation.id == reservation_id
        assert reservation.status == ReservationStatus.CONFIRMED
        assert reservation.customer_name == "Jonas"
        assert reservation.deleted_at is None

    def test_status_defaults_to_pending(self):
        """Test: Status wird auf PENDING gesetzt wenn nicht angegeben"""
        now = datetime.now(timezone.utc)
        data = {
            "id": uuid4(),
            "customer_name": "Jonas",
            "customer_email": "jonas@example.com",
            "reservation_date": now + timedelta(days=1),
            "party_size": 4,
            "created_at": now,
            "updated_at": now
        }
        reservation = Reservation(**data)
        
        assert reservation.status == ReservationStatus.PENDING

    def test_deleted_at_optional(self):
        """Test: deleted_at ist optional und standardmäßig None"""
        now = datetime.now(timezone.utc)
        data = {
            "id": uuid4(),
            "customer_name": "Jonas",
            "customer_email": "jonas@example.com",
            "reservation_date": now + timedelta(days=1),
            "party_size": 4,
            "created_at": now,
            "updated_at": now
        }
        reservation = Reservation(**data)
        
        assert reservation.deleted_at is None

    def test_soft_delete_with_deleted_at(self):
        """Test: Soft Delete durch Setzen von deleted_at"""
        now = datetime.now(timezone.utc)
        data = {
            "id": uuid4(),
            "customer_name": "Jonas",
            "customer_email": "jonas@example.com",
            "reservation_date": now + timedelta(days=1),
            "party_size": 4,
            "created_at": now,
            "updated_at": now,
            "deleted_at": now
        }
        reservation = Reservation(**data)
        
        assert reservation.deleted_at == now

    def test_all_status_values(self):
        """Test: Alle ReservationStatus Werte sind valide"""
        now = datetime.now(timezone.utc)
        statuses = [
            ReservationStatus.PENDING,
            ReservationStatus.CONFIRMED,
            ReservationStatus.CANCELLED,
            ReservationStatus.COMPLETED
        ]
        
        for status_value in statuses:
            data = {
                "id": uuid4(),
                "customer_name": "Test User",
                "customer_email": "test@example.com",
                "reservation_date": now + timedelta(days=1),
                "party_size": 2,
                "status": status_value,
                "created_at": now,
                "updated_at": now
            }
            reservation = Reservation(**data)
            assert reservation.status == status_value


class TestReservationStatus:
    """Unit Tests für ReservationStatus Enum"""

    def test_status_enum_values(self):
        """Test: Alle Status-Werte sind korrekt definiert"""
        assert ReservationStatus.PENDING.value == "pending"
        assert ReservationStatus.CONFIRMED.value == "confirmed"
        assert ReservationStatus.CANCELLED.value == "cancelled"
        assert ReservationStatus.COMPLETED.value == "completed"

    def test_status_string_comparison(self):
        """Test: Status-Vergleich mit Strings funktioniert"""
        assert ReservationStatus.PENDING == "pending"
        assert ReservationStatus.CONFIRMED == "confirmed"


class TestDefaultRoomId:
    """Unit Tests für DEFAULT_ROOM_ID Konstante"""

    def test_default_room_id_format(self):
        """Test: DEFAULT_ROOM_ID ist eine valide UUID"""
        assert DEFAULT_ROOM_ID == "00000000-0000-0000-0000-000000000000"
        
        # Verifiziere dass es als UUID geparst werden kann
        try:
            UUID(DEFAULT_ROOM_ID)
        except ValueError:
            pytest.fail("DEFAULT_ROOM_ID ist keine valide UUID")
