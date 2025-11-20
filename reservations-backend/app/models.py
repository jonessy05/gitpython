"""
Pydantic models for Reservations API
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class ReservationBase(BaseModel):
    """Base Schema for Reservations"""
    start_date: date = Field(..., alias="from", description="Start date of the reservation")
    end_date: date = Field(..., alias="to", description="End date of the reservation")
    room_id: UUID = Field(..., description="ID of the room")

    model_config = ConfigDict(populate_by_name=True)


class ReservationCreate(ReservationBase):
    """Schema for creating a reservation"""
    pass


class Reservation(ReservationBase):
    """Schema for a full reservation"""
    id: UUID = Field(..., description="Unique ID of the reservation")
    deleted_at: Optional[datetime] = Field(None, description="Timestamp when the reservation was soft-deleted")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TokenData(BaseModel):
    """JWT Token Payload"""
    sub: str = Field(..., description="Subject (Benutzer-ID)")
    exp: int = Field(..., description="Expiration Time")

