from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
import os

# Create the FastAPI app instance FIRST
app = FastAPI(title="CivicShield API", description="Privacy-Preserving Surveillance System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup (simplified for now)
from .database import SessionLocal, init_db
from .models import Event, UnlockRequest
from .storage import encrypt_file, decrypt_file
from .config import EDGE_MODE, TOTAL_BANDWIDTH_USED
import backend.config as config

# Initialize database
init_db()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------
# Schemas
# ---------------------------

class EventSchema(BaseModel):
    event_id: str
    event_type: str
    confidence: float
    timestamp: datetime
    raw_clip_path: str

    class Config:
        from_attributes = True


class ModeSchema(BaseModel):
    edge_mode: bool


class UnlockSchema(BaseModel):
    event_id: str
    requested_by: str


# ---------------------------
# Routes
# ---------------------------

@app.get("/")
def root():
    return {"message": "CivicShield API is running", "status": "active"}


@app.post("/event")
def receive_event(event: EventSchema):
    db = SessionLocal()

    db_event = Event(
        event_id=event.event_id,
        event_type=event.event_type,
        confidence=event.confidence,
        timestamp=event.timestamp,
        raw_clip_path=event.raw_clip_path,
        encrypted=False,
        unlocked=False
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # Encrypt raw clip
    encrypt_file(event.raw_clip_path)
    db_event.encrypted = True
    db.commit()

    # Bandwidth simulation
    if config.EDGE_MODE:
        config.TOTAL_BANDWIDTH_USED += 300
    else:
        config.TOTAL_BANDWIDTH_USED += 5_000_000

    db.close()

    return {"status": "event stored and encrypted", "event_id": event.event_id}


@app.get("/events")
def get_events():
    db = SessionLocal()
    events = db.query(Event).all()
    db.close()
    return events


@app.post("/request-unlock")
def request_unlock(data: UnlockSchema):
    db = SessionLocal()

    event = db.query(Event).filter(Event.event_id == data.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    existing_request = db.query(UnlockRequest).filter(
        UnlockRequest.event_id == data.event_id
    ).first()

    if existing_request:
        existing_request.approval_count += 1
        if existing_request.approval_count >= 2:
            existing_request.approved = True
            decrypt_file(event.raw_clip_path)
            event.unlocked = True
    else:
        new_request = UnlockRequest(
            event_id=data.event_id,
            requested_by=data.requested_by,
            approval_count=1
        )
        db.add(new_request)

    db.commit()
    db.close()

    return {"status": "unlock request processed"}


@app.get("/unlock-status/{event_id}")
def unlock_status(event_id: str):
    db = SessionLocal()
    event = db.query(Event).filter(Event.event_id == event_id).first()
    db.close()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return {
        "unlocked": event.unlocked,
        "encrypted": event.encrypted
    }


@app.post("/mode")
def set_mode(mode: ModeSchema):
    config.EDGE_MODE = mode.edge_mode
    return {"edge_mode": config.EDGE_MODE}


@app.get("/mode")
def get_mode():
    return {
        "edge_mode": config.EDGE_MODE,
        "total_bandwidth_used_bytes": config.TOTAL_BANDWIDTH_USED
    }