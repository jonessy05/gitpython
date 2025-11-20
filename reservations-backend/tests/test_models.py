"""
Unit Tests für Pydantic Models
Testet Validierung, Default-Werte und Constraints
"""
import pytest
from datetime import date, datetime, timezone, timedelta
from uuid import uuid4, UUID
from pydantic import ValidationError

from app.models import (
    ReservationBase,
    ReservationCreate,
    Reservation
)


class TestReservationBase:
    """Unit Tests für ReservationBase Model"""

    def test_valid_reservation_base(self):
        """Test: Valides ReservationBase Model erstellen"""
        data = {
            "from": date.today(),
            "to": date.today() + timedelta(days=1),
            "room_id": uuid4()
        }
        reservation = ReservationBase(**data)
        
        assert reservation.start_date == date.today()
        assert reservation.end_date == date.today() + timedelta(days=1)
        assert isinstance(reservation.room_id, UUID)

    def test_reservation_with_alias(self):
        """Test: Model akzeptiert 'from' und 'to' als Alias"""
        room_uuid = uuid4()
        data = {
            "from": "2025-12-01",
            "to": "2025-12-02",
            "room_id": str(room_uuid)
        }
        reservation = ReservationBase(**data)
        
        assert reservation.start_date == date(2025, 12, 1)
        assert reservation.end_date == date(2025, 12, 2)
        assert reservation.room_id == room_uuid

    def test_room_id_validation(self):
        """Test: room_id muss eine valide UUID sein"""
        data = {
            "from": date.today(),
            "to": date.today() + timedelta(days=1),
            "room_id": "not-a-uuid"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ReservationBase(**data)
        
        assert "room_id" in str(exc_info.value)

    def test_date_validation(self):
        """Test: from und to müssen valide Daten sein"""
        data = {
            "from": "invalid-date",
            "to": date.today(),
            "room_id": uuid4()
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ReservationBase(**data)
        
        assert "from" in str(exc_info.value) or "start_date" in str(exc_info.value)


class TestReservationCreate:
    """Unit Tests für ReservationCreate Model"""

    def test_valid_reservation_create(self):
        """Test: Valides ReservationCreate Model erstellen"""
        data = {
            "from": date.today() + timedelta(days=7),
            "to": date.today() + timedelta(days=10),
            "room_id": uuid4()
        }
        reservation = ReservationCreate(**data)
        
        assert reservation.start_date == date.today() + timedelta(days=7)
        assert reservation.end_date == date.today() + timedelta(days=10)


class TestReservation:
    """Unit Tests für vollständiges Reservation Model"""

    def test_valid_reservation(self):
        """Test: Vollständiges Reservation Model mit allen Feldern"""
        reservation_id = uuid4()
        room_uuid = uuid4()
        start = date.today()
        end = date.today() + timedelta(days=5)
        
        data = {
            "id": reservation_id,
            "from": start,
            "to": end,
            "room_id": room_uuid
        }
        reservation = Reservation(**data)
        
        assert reservation.id == reservation_id
        assert reservation.start_date == start
        assert reservation.end_date == end
        assert reservation.room_id == room_uuid
        assert reservation.deleted_at is None

    def test_deleted_at_optional(self):
        """Test: deleted_at ist optional und standardmäßig None"""
        data = {
            "id": uuid4(),
            "from": date.today(),
            "to": date.today() + timedelta(days=1),
            "room_id": uuid4()
        }
        reservation = Reservation(**data)
        
        assert reservation.deleted_at is None

    def test_soft_delete_with_deleted_at(self):
        """Test: Soft Delete durch Setzen von deleted_at"""
        now = datetime.now(timezone.utc)
        data = {
            "id": uuid4(),
            "from": date.today(),
            "to": date.today() + timedelta(days=1),
            "room_id": uuid4(),
            "deleted_at": now
        }
        reservation = Reservation(**data)
        
        assert reservation.deleted_at == now

    def test_model_dump_uses_aliases(self):
        """Test: model_dump verwendet Aliase (from/to) statt Feldnamen"""
        data = {
            "id": uuid4(),
            "from": date.today(),
            "to": date.today() + timedelta(days=1),
            "room_id": uuid4()
        }
        reservation = Reservation(**data)
        dumped = reservation.model_dump(by_alias=True)
        
        assert "from" in dumped
        assert "to" in dumped
        assert "id" in dumped
        assert "room_id" in dumped

