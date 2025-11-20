"""
Routes for Reservations API
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import Reservation, ReservationCreate
from app.auth import verify_token
from app.logging_config import log_operation
from app import database

router = APIRouter(
    prefix="/api/v3/reservations",
    tags=["reservations"]
)


@router.get("/status")
async def get_status():
    """
    Status information about the API
    """
    return {
        "authors": ["Biletado Team"],
        "api_version": "3.0.0"
    }


@router.get("/health")
async def get_health():
    """
    Health check endpoint
    """
    return {"live": True, "ready": True}


@router.get("/health/live")
async def get_health_live():
    """
    Liveness check endpoint
    """
    return {"live": True}


@router.get("/health/ready")
async def get_health_ready():
    """
    Readiness check endpoint
    """
    return {"ready": True}


@router.get("/reservations", response_model=Dict[str, List[Reservation]])
async def get_all_reservations(
    include_deleted: bool = Query(False, description="Include deleted reservations"),
    user_id: str = Depends(verify_token),
    db: Session = Depends(database.get_db)
):
    """
    Get all reservations
    """
    reservations = database.get_all_reservations(db, include_deleted=include_deleted)
    
    log_operation(
        operation="READ",
        user_id=user_id,
        object_type="reservation",
        object_id="all",
        message=f"Retrieved {len(reservations)} reservations"
    )
    
    return {"reservations": reservations}


@router.get("/reservations/{reservation_id}", response_model=Reservation)
async def get_reservation(
    reservation_id: UUID,
    user_id: str = Depends(verify_token),
    db: Session = Depends(database.get_db)
):
    """
    Get a single reservation by ID
    """
    reservation = database.get_reservation_by_id(db, reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not found", "message": f"Reservation with ID {reservation_id} not found"}
        )
    
    log_operation(
        operation="READ",
        user_id=user_id,
        object_type="reservation",
        object_id=str(reservation_id),
        message=f"Retrieved reservation {reservation_id}"
    )
    
    return reservation


@router.post("/reservations", response_model=Reservation, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    reservation: ReservationCreate,
    user_id: str = Depends(verify_token),
    db: Session = Depends(database.get_db)
):
    """
    Create a new reservation
    """
    reservation_data = reservation.model_dump(by_alias=True)
    new_reservation = database.create_reservation(db, reservation_data)
    
    log_operation(
        operation="CREATE",
        user_id=user_id,
        object_type="reservation",
        object_id=str(new_reservation.id),
        message=f"Created reservation {new_reservation.id}"
    )
    
    return new_reservation


@router.put("/reservations/{reservation_id}", response_model=Reservation)
async def replace_reservation(
    reservation_id: UUID,
    reservation: ReservationCreate,
    user_id: str = Depends(verify_token),
    db: Session = Depends(database.get_db)
):
    """
    Create, replace or restore a reservation by ID
    """
    existing = database.get_reservation_by_id(db, reservation_id)
    reservation_data = reservation.model_dump(by_alias=True)
    
    if existing:
        # Update
        updated = database.update_reservation(db, reservation_id, reservation_data)
        # Restore if deleted
        if existing.deleted_at:
             database.restore_reservation(db, reservation_id)
             updated = database.get_reservation_by_id(db, reservation_id)

        log_operation(
            operation="UPDATE",
            user_id=user_id,
            object_type="reservation",
            object_id=str(reservation_id),
            message=f"Updated/restored reservation {reservation_id}"
        )
        return updated
    else:
        # Create with ID
        reservation_data["id"] = reservation_id
        new_reservation = database.create_reservation(db, reservation_data)
        
        log_operation(
            operation="CREATE",
            user_id=user_id,
            object_type="reservation",
            object_id=str(reservation_id),
            message=f"Created reservation with specified ID {reservation_id}"
        )
        return new_reservation


@router.delete("/reservations/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(
    reservation_id: UUID,
    user_id: str = Depends(verify_token),
    db: Session = Depends(database.get_db)
):
    """
    Soft delete a reservation
    """
    if not database.get_reservation_by_id(db, reservation_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not found", "message": f"Reservation with ID {reservation_id} not found"}
        )
    
    database.delete_reservation(db, reservation_id)
    
    log_operation(
        operation="DELETE",
        user_id=user_id,
        object_type="reservation",
        object_id=str(reservation_id),
        message=f"Deleted reservation {reservation_id}"
    )

