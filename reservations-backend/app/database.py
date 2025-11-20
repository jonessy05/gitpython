"""
PostgreSQL Database Connection and Models
"""
import os
from sqlalchemy import create_engine, Column, Date, DateTime, Uuid
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.sql import func
from uuid import uuid4, UUID
from typing import List, Optional
from datetime import datetime

# Database Configuration
DB_USER = os.getenv("POSTGRES_RESERVATIONS_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_RESERVATIONS_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_RESERVATIONS_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_RESERVATIONS_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_RESERVATIONS_DBNAME", "reservations_v3")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ReservationDB(Base):
    __tablename__ = "reservations"

    id = Column(Uuid, primary_key=True, default=uuid4)
    start_date = Column("from", Date, nullable=False)
    end_date = Column("to", Date, nullable=False)
    room_id = Column(Uuid, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD Operations
def get_all_reservations(db: Session, include_deleted: bool = False) -> List[ReservationDB]:
    query = db.query(ReservationDB)
    if not include_deleted:
        query = query.filter(ReservationDB.deleted_at.is_(None))
    return query.all()

def get_reservation_by_id(db: Session, reservation_id: UUID) -> Optional[ReservationDB]:
    return db.query(ReservationDB).filter(ReservationDB.id == reservation_id).first()

def create_reservation(db: Session, reservation_data: dict) -> ReservationDB:
    # Ensure keys match the model attributes (start_date, end_date)
    # If input has 'from'/'to', map them
    data = reservation_data.copy()
    if 'from' in data:
        data['start_date'] = data.pop('from')
    if 'to' in data:
        data['end_date'] = data.pop('to')
        
    db_reservation = ReservationDB(**data)
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

def update_reservation(db: Session, reservation_id: UUID, updates: dict) -> Optional[ReservationDB]:
    db_reservation = get_reservation_by_id(db, reservation_id)
    if not db_reservation:
        return None
    
    # Map 'from'/'to' to start_date/end_date
    if 'from' in updates:
        updates['start_date'] = updates.pop('from')
    if 'to' in updates:
        updates['end_date'] = updates.pop('to')

    for key, value in updates.items():
        if hasattr(db_reservation, key):
            setattr(db_reservation, key, value)
    
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

def delete_reservation(db: Session, reservation_id: UUID) -> bool:
    db_reservation = get_reservation_by_id(db, reservation_id)
    if not db_reservation:
        return False
    
    db_reservation.deleted_at = func.now()
    db.commit()
    return True

def restore_reservation(db: Session, reservation_id: UUID) -> bool:
    db_reservation = get_reservation_by_id(db, reservation_id)
    if not db_reservation:
        return False
        
    db_reservation.deleted_at = None
    db.commit()
    return True

