"""
In-Memory Datenbank für Reservierungen
Diese Datei verwaltet den Datenspeicher. Für Produktion sollte dies durch
eine echte PostgreSQL/MySQL Datenbank mit SQLAlchemy ORM ersetzt werden.
"""
from datetime import datetime, timezone
from typing import Dict, Optional
from uuid import UUID, uuid4
from app.models import ReservationStatus, DEFAULT_ROOM_ID
import logging

logger = logging.getLogger(__name__)

# In-Memory Datenbank
_reservations_db: Dict[UUID, dict] = {}


def init_db():
    """Initialisiert die In-Memory Datenbank mit Sample-Daten"""
    global _reservations_db

    sample_id = uuid4()
    deleted_id = uuid4()
    
    now = datetime.now(timezone.utc)
    
    _reservations_db = {
        sample_id: {
            "id": sample_id,
            "customer_name": "Jonas",
            "customer_email": "jonas@example.com",
            "reservation_date": datetime(2025, 11, 10, 19, 0, 0, tzinfo=timezone.utc),
            "party_size": 4,
            "special_requests": None,
            "room_id": "11111111-1111-1111-1111-111111111111",
            "status": ReservationStatus.CONFIRMED,
            "created_at": now,
            "updated_at": now,
            "deleted_at": None
        },
        deleted_id: {
            "id": deleted_id,
            "customer_name": "Deleted User",
            "customer_email": "deleted@example.com",
            "reservation_date": datetime(2025, 11, 5, 18, 0, 0, tzinfo=timezone.utc),
            "party_size": 2,
            "special_requests": None,
            "room_id": "22222222-2222-2222-2222-222222222222",
            "status": ReservationStatus.CANCELLED,
            "created_at": now,
            "updated_at": now,
            "deleted_at": now
        }
    }
    logger.info("Database initialized with sample data")


def get_all_reservations(include_deleted: bool = False) -> list:
    """Gibt alle Reservierungen zurück"""
    if include_deleted:
        return list(_reservations_db.values())
    return [res for res in _reservations_db.values() if res.get("deleted_at") is None]


def get_reservation_by_id(reservation_id: UUID) -> Optional[dict]:
    """Gibt eine Reservierung nach ID zurück oder None"""
    return _reservations_db.get(reservation_id)


def create_reservation(reservation_data: dict) -> dict:
    """Erstellt eine neue Reservierung und gibt sie zurück"""
    new_id = uuid4()
    
    new_reservation = {
        "id": new_id,
        "deleted_at": None,
        **reservation_data
    }
    if not new_reservation.get("room_id"):
        new_reservation["room_id"] = DEFAULT_ROOM_ID

    _reservations_db[new_id] = new_reservation

    logger.debug(f"Created reservation with id: {new_reservation['id']}")
    return new_reservation


def update_reservation(reservation_id: UUID, updates: dict) -> Optional[dict]:
    """Aktualisiert eine Reservierung"""
    if reservation_id not in _reservations_db:
        return None

    _reservations_db[reservation_id].update(updates)
    logger.debug(f"Updated reservation with id: {reservation_id}")
    return _reservations_db[reservation_id]


def delete_reservation(reservation_id: UUID) -> bool:
    """Soft delete einer Reservierung. Gibt True zurück wenn erfolgreich, False sonst"""
    if reservation_id not in _reservations_db:
        return False

    _reservations_db[reservation_id]["deleted_at"] = datetime.now(timezone.utc)
    logger.debug(f"Soft deleted reservation with id: {reservation_id}")
    return True


def reservation_exists(reservation_id: UUID) -> bool:
    """Prüft ob eine Reservierung existiert (auch gelöschte)"""
    return reservation_id in _reservations_db


# Initialisiere DB beim Import
init_db()
