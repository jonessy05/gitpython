"""
Routes für Reservierungen API
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from datetime import datetime, timezone
from uuid import UUID
from app.models import Reservation, ReservationCreate, ReservationStatus, DEFAULT_ROOM_ID
from app.auth import verify_token
from app.logging_config import log_operation
from app import database

router = APIRouter(
    prefix="/api/v3/reservations",
    tags=["reservations"]
)


@router.get("/reservations")
async def get_all_reservations(
    include_deleted: bool = Query(False, description="Include deleted reservations"),
    user_id: str = Depends(verify_token)
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Alle Reservierungen abrufen (für authentifizierte Benutzer)
    
    Returns object with 'reservations' array containing all reservations.
    """
    reservations = database.get_all_reservations(include_deleted=include_deleted)
    
    # Log the read operation
    log_operation(
        operation="READ",
        user_id=user_id,
        object_type="reservation",
        object_id="all",
        message=f"Retrieved {len(reservations)} reservations"
    )
    
    result = []
    for res in reservations:
        # create pydantic model to ensure types, then dump to dict
        r = Reservation(**res).model_dump()
        rd = r.get("reservation_date")
        # ensure `from` and `to` fields are present (Quickstart/OpenAPI expectation)
        try:
            if isinstance(rd, datetime):
                r["from"] = rd.date().isoformat()
                r["to"] = rd.date().isoformat()
            else:
                r["from"] = str(rd)
                r["to"] = str(rd)
        except Exception:
            r["from"] = str(rd)
            r["to"] = str(rd)
        # ensure room_id exists even for legacy data lacking the field
        r["room_id"] = str(r.get("room_id") or res.get("room_id") or DEFAULT_ROOM_ID)
        result.append(r)

    return {
        "reservations": result
    }


@router.get("/reservations/{reservation_id}")
async def get_reservation(
    reservation_id: UUID,
    user_id: str = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Einzelne Reservierung nach ID abrufen
    """
    reservation = database.get_reservation_by_id(reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not found", "message": f"Reservierung mit ID {reservation_id} nicht gefunden"}
        )
    
    # Log the read operation
    log_operation(
        operation="READ",
        user_id=user_id,
        object_type="reservation",
        object_id=str(reservation_id),
        message=f"Retrieved reservation {reservation_id}"
    )
    
    r = Reservation(**reservation).model_dump()
    rd = r.get("reservation_date")
    try:
        if isinstance(rd, datetime):
            r["from"] = rd.date().isoformat()
            r["to"] = rd.date().isoformat()
        else:
            r["from"] = str(rd)
            r["to"] = str(rd)
    except Exception:
        r["from"] = str(rd)
        r["to"] = str(rd)
    # ensure room_id exists for single responses as well
    r["room_id"] = str(r.get("room_id") or reservation.get("room_id") or DEFAULT_ROOM_ID)

    return r


@router.post("/reservations", response_model=Reservation, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    reservation: ReservationCreate,
    user_id: str = Depends(verify_token)
) -> Reservation:
    """
    Neue Reservierung erstellen (authentifiziert)
    
    Validates all input data including email format and future reservation dates.
    """
    now = datetime.now(timezone.utc)
    room_id = reservation.room_id or DEFAULT_ROOM_ID
    new_reservation_data = {
        "customer_name": reservation.customer_name,
        "customer_email": str(reservation.customer_email),
        "reservation_date": reservation.reservation_date,
        "party_size": reservation.party_size,
        "special_requests": reservation.special_requests,
        "room_id": room_id,
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


@router.put("/reservations/{reservation_id}", response_model=Reservation)
async def update_reservation(
    reservation_id: UUID,
    reservation: ReservationCreate,
    user_id: str = Depends(verify_token)
) -> Reservation:
    """
    Reservierung aktualisieren oder wiederherstellen (create, replace and/or restore)
    
    If reservation exists (even if deleted), it will be updated/restored.
    If reservation doesn't exist, a new one will be created with the specified ID.
    """
    existing = database.get_reservation_by_id(reservation_id)
    now = datetime.now(timezone.utc)
    
    if existing:
        # Update existing reservation
        room_id = reservation.room_id or DEFAULT_ROOM_ID
        updates = {
            "customer_name": reservation.customer_name,
            "customer_email": str(reservation.customer_email),
            "reservation_date": reservation.reservation_date,
            "party_size": reservation.party_size,
            "special_requests": reservation.special_requests,
            "room_id": room_id,
            "updated_at": now,
            "deleted_at": None  # Restore if it was deleted
        }
        
        updated = database.update_reservation(reservation_id, updates)
        
        # Audit-Log
        log_operation(
            operation="UPDATE",
            user_id=user_id,
            object_type="reservation",
            object_id=str(reservation_id),
            message=f"Updated/restored reservation {reservation_id}"
        )
        
        return Reservation(**updated)
    else:
        # Create new reservation with specific ID
        room_id = reservation.room_id or DEFAULT_ROOM_ID
        new_reservation_data = {
            "id": reservation_id,
            "customer_name": reservation.customer_name,
            "customer_email": str(reservation.customer_email),
            "reservation_date": reservation.reservation_date,
            "party_size": reservation.party_size,
            "special_requests": reservation.special_requests,
            "room_id": room_id,
            "status": ReservationStatus.PENDING,
            "created_at": now,
            "updated_at": now,
            "deleted_at": None
        }
        
        database._reservations_db[reservation_id] = new_reservation_data
        
        # Audit-Log
        log_operation(
            operation="CREATE",
            user_id=user_id,
            object_type="reservation",
            object_id=str(reservation_id),
            message=f"Created reservation with specified ID {reservation_id}"
        )
        
        return Reservation(**new_reservation_data)


@router.patch("/{reservation_id}/status", response_model=Reservation)
async def update_reservation_status(
    reservation_id: UUID,
    new_status: ReservationStatus,
    user_id: str = Depends(verify_token)
) -> Reservation:
    """
    Status einer Reservierung aktualisieren
    """
    if not database.reservation_exists(reservation_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not found", "message": f"Reservierung mit ID {reservation_id} nicht gefunden"}
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
    reservation_id: UUID,
    user_id: str = Depends(verify_token)
) -> None:
    """
    Reservierung löschen (soft delete)
    """
    if not database.reservation_exists(reservation_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not found", "message": f"Reservierung mit ID {reservation_id} nicht gefunden"}
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
