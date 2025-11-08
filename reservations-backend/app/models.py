"""
Datenbankmodelle für Reservierungen
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ReservationStatus(str, Enum):
    """Status einer Reservierung"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ReservationBase(BaseModel):
    """Basis-Schema für Reservierungen"""
    customer_name: str = Field(..., min_length=1, description="Name des Kunden")
    customer_email: str = Field(..., description="E-Mail des Kunden")
    reservation_date: datetime = Field(..., description="Reservierungsdatum")
    party_size: int = Field(..., gt=0, description="Anzahl der Personen")
    special_requests: Optional[str] = Field(None, description="Spezielle Wünsche")


class ReservationCreate(ReservationBase):
    """Schema zum Erstellen einer Reservierung"""
    pass


class Reservation(ReservationBase):
    """Vollständiges Reservierungs-Schema mit ID und Status"""
    id: int = Field(..., description="Eindeutige Reservierungs-ID")
    status: ReservationStatus = Field(default=ReservationStatus.PENDING, description="Status der Reservierung")
    created_at: datetime = Field(..., description="Erstellungsdatum")
    updated_at: datetime = Field(..., description="Zuletzt aktualisiert")

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    """JWT Token Payload"""
    sub: str = Field(..., description="Subject (Benutzer-ID)")
    exp: int = Field(..., description="Expiration Time")
