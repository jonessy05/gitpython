"""
Routes für Reservierungen API
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime, timezone
from app.models import Reservation, ReservationCreate, ReservationStatus
from app.auth import verify_token
from app.logging_config import log_operation
from app import database

router = APIRouter(
    prefix="/reservations",
    tags=["reservations"]
)


@router.get("/", response_model=List[Reservation])
async def get_all_reservations(user_id: str = Depends(verify_token)) -> List[Reservation]:
    """
    Alle Reservierungen abrufen (für authentifizierte Benutzer)
    """
    reservations = database.get_all_reservations()
    return [Reservation(**res) for res in reservations]


@router.get("/{reservation_id}", response_model=Reservation)
async def get_reservation(
    reservation_id: int,
    user_id: str = Depends(verify_token)
) -> Reservation:
    """
    Einzelne Reservierung nach ID abrufen
    """
    reservation = database.get_reservation_by_id(reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservierung mit ID {reservation_id} nicht gefunden"
        )
    
    return Reservation(**reservation)


@router.post("/", response_model=Reservation, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    reservation: ReservationCreate,
    user_id: str = Depends(verify_token)
) -> Reservation:
    """
    Neue Reservierung erstellen (authentifiziert)
    """
    now = datetime.now(timezone.utc)
    new_reservation_data = {
        "customer_name": reservation.customer_name,
        "customer_email": reservation.customer_email,
        "reservation_date": reservation.reservation_date,
        "party_size": reservation.party_size,
        "special_requests": reservation.special_requests,
        "status": ReservationStatus.PENDING,
        "created_at": now,
        "updated_at": now
    }
    
    new_reservation = database.create_reservation(new_reservation_data)
    
    # Audit-Log
    log_operation(
        operation="CREATE",
        user_id=user_id,
        object_type="reservation",
        object_id=str(new_reservation["id"]),
        message=f"Created reservation for {reservation.customer_name}"
    )
    
    return Reservation(**new_reservation)


@router.put("/{reservation_id}", response_model=Reservation)
async def update_reservation(
    reservation_id: int,
    reservation: ReservationCreate,
    user_id: str = Depends(verify_token)
) -> Reservation:
    """
    Reservierung aktualisieren
    """
    if not database.reservation_exists(reservation_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservierung mit ID {reservation_id} nicht gefunden"
        )
    
    updates = {
        "customer_name": reservation.customer_name,
        "customer_email": reservation.customer_email,
        "reservation_date": reservation.reservation_date,
        "party_size": reservation.party_size,
        "special_requests": reservation.special_requests,
        "updated_at": datetime.now(timezone.utc)
    }
    
    updated = database.update_reservation(reservation_id, updates)
    
    # Audit-Log
    log_operation(
        operation="UPDATE",
        user_id=user_id,
        object_type="reservation",
        object_id=str(reservation_id),
        message=f"Updated reservation {reservation_id}"
    )
    
    return Reservation(**updated)


@router.patch("/{reservation_id}/status", response_model=Reservation)
async def update_reservation_status(
    reservation_id: int,
    new_status: ReservationStatus,
    user_id: str = Depends(verify_token)
) -> Reservation:
    """
    Status einer Reservierung aktualisieren
    """
    if not database.reservation_exists(reservation_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservierung mit ID {reservation_id} nicht gefunden"
        )
    
    updates = {
        "status": new_status,
        "updated_at": datetime.now(timezone.utc)
    }
    
    updated = database.update_reservation(reservation_id, updates)
    
    # Audit-Log
    log_operation(
        operation="UPDATE",
        user_id=user_id,
        object_type="reservation",
        object_id=str(reservation_id),
        message=f"Updated reservation status to {new_status}"
    )
    
    return Reservation(**updated)


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(
    reservation_id: int,
    user_id: str = Depends(verify_token)
) -> None:
    """
    Reservierung löschen
    """
    if not database.reservation_exists(reservation_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservierung mit ID {reservation_id} nicht gefunden"
        )
    
    # Audit-Log vor dem Löschen
    log_operation(
        operation="DELETE",
        user_id=user_id,
        object_type="reservation",
        object_id=str(reservation_id),
        message=f"Deleted reservation {reservation_id}"
    )
    
    database.delete_reservation(reservation_id)
