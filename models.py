from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from .database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)
    event_type = Column(String)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    raw_clip_path = Column(String)
    encrypted = Column(Boolean, default=False)
    unlocked = Column(Boolean, default=False)


class UnlockRequest(Base):
    __tablename__ = "unlock_requests"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, index=True)
    requested_by = Column(String)
    approved = Column(Boolean, default=False)
    approval_count = Column(Integer, default=1)
    request_time = Column(DateTime, default=datetime.utcnow)