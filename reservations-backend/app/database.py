"""
In-Memory Datenbank für Reservierungen
Diese Datei verwaltet den Datenspeicher. Für Produktion sollte dies durch
eine echte PostgreSQL/MySQL Datenbank mit SQLAlchemy ORM ersetzt werden.
"""
from datetime import datetime, timezone
from typing import Dict, Optional
from app.models import ReservationStatus
import logging

logger = logging.getLogger(__name__)

# In-Memory Datenbank
_reservations_db: Dict = {}
_next_id: int = 2  # Start bei 2, da 1 schon als Sample existiert


def init_db():
    """Initialisiert die In-Memory Datenbank mit Sample-Daten"""
    global _reservations_db, _next_id

    _reservations_db = {
        1: {
            "id": 1,
            "customer_name": "Jonas",
            "customer_email": "jonas@example.com",
            "reservation_date": datetime(2025, 11, 10, 19, 0, 0, tzinfo=timezone.utc),
            "party_size": 4,
            "special_requests": None,
            "status": ReservationStatus.CONFIRMED,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    }
    _next_id = 2
    logger.info("Database initialized with sample data")


def get_all_reservations() -> list:
    """Gibt alle Reservierungen zurück"""
    return list(_reservations_db.values())


def get_reservation_by_id(reservation_id: int) -> Optional[dict]:
    """Gibt eine Reservierung nach ID zurück oder None"""
    return _reservations_db.get(reservation_id)


def create_reservation(reservation_data: dict) -> dict:
    """Erstellt eine neue Reservierung und gibt sie zurück"""
    global _next_id

    new_reservation = {
        "id": _next_id,
        **reservation_data
    }

    _reservations_db[_next_id] = new_reservation
    _next_id += 1

    logger.debug(f"Created reservation with id: {new_reservation['id']}")
    return new_reservation


def update_reservation(reservation_id: int, updates: dict) -> Optional[dict]:
    """Aktualisiert eine Reservierung"""
    if reservation_id not in _reservations_db:
        return None

    _reservations_db[reservation_id].update(updates)
    logger.debug(f"Updated reservation with id: {reservation_id}")
    return _reservations_db[reservation_id]


def delete_reservation(reservation_id: int) -> bool:
    """Löscht eine Reservierung. Gibt True zurück wenn erfolgreich, False sonst"""
    if reservation_id not in _reservations_db:
        return False

    del _reservations_db[reservation_id]
    logger.debug(f"Deleted reservation with id: {reservation_id}")
    return True


def reservation_exists(reservation_id: int) -> bool:
    """Prüft ob eine Reservierung existiert"""
    return reservation_id in _reservations_db


# Initialisiere DB beim Import
init_db()
