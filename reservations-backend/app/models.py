"""
Datenbankmodelle für Reservierungen
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import UUID


DEFAULT_ROOM_ID = "00000000-0000-0000-0000-000000000000"


class ReservationStatus(str, Enum):
    """Status einer Reservierung"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ReservationBase(BaseModel):
    """Basis-Schema für Reservierungen"""
    customer_name: str = Field(..., min_length=1, max_length=200, description="Name des Kunden")
    customer_email: EmailStr = Field(..., description="E-Mail des Kunden")
    reservation_date: datetime = Field(..., description="Reservierungsdatum")
    party_size: int = Field(..., gt=0, le=100, description="Anzahl der Personen")
    special_requests: Optional[str] = Field(None, max_length=1000, description="Spezielle Wünsche")
    room_id: str = Field(
        default=DEFAULT_ROOM_ID,
        min_length=1,
        max_length=100,
        description="Raum-ID, in dem die Reservierung stattfindet"
    )

    @field_validator("room_id", mode="before")
    @classmethod
    def ensure_room_id(cls, value: Optional[str]) -> str:
        """Normalisiert fehlende oder leere Raum-IDs auf einen Standardwert"""
        if value is None:
            return DEFAULT_ROOM_ID
        normalized = str(value).strip()
        return normalized or DEFAULT_ROOM_ID
    


class ReservationCreate(ReservationBase):
    """Schema zum Erstellen einer Reservierung"""
    @field_validator('reservation_date')
    @classmethod
    def validate_reservation_date(cls, v: datetime) -> datetime:
        """Ensure reservation date is not in the past when creating a reservation"""
        # allow loading existing reservations with past dates; enforce only on creation
        if v < datetime.now(v.tzinfo or None):
            raise ValueError('Reservation date cannot be in the past')
        return v


class Reservation(ReservationBase):
    """Vollständiges Reservierungs-Schema mit ID und Status"""
    id: UUID = Field(..., description="Eindeutige Reservierungs-ID (UUID)")
    status: ReservationStatus = Field(default=ReservationStatus.PENDING, description="Status der Reservierung")
    created_at: datetime = Field(..., description="Erstellungsdatum")
    updated_at: datetime = Field(..., description="Zuletzt aktualisiert")
    deleted_at: Optional[datetime] = Field(None, description="Löschdatum (für soft delete)")

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    """JWT Token Payload"""
    sub: str = Field(..., description="Subject (Benutzer-ID)")
    exp: int = Field(..., description="Expiration Time")
