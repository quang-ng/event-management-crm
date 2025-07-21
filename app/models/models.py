# SQLAlchemy models for User and Event
import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class UserRole(str, enum.Enum):
    attendee = "attendee"
    host = "host"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    avatar = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    company = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.attendee)
    events_hosted = Column(Integer, default=0)
    events_attended = Column(Integer, default=0)
    events_participated = relationship("EventRegistration", back_populates="user")
    events_owned = relationship("Event", back_populates="owner", foreign_keys='Event.owner_id')
    events_hosting = relationship(
        "EventHost",
        back_populates="user"
    )

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    venue = Column(String, nullable=True)
    max_capacity = Column(Integer, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="events_owned", foreign_keys=[owner_id])
    hosts = relationship(
        "EventHost",
        back_populates="event"
    )
    registrations = relationship("EventRegistration", back_populates="event")

class EventRegistration(Base):
    __tablename__ = "event_registrations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    user = relationship("User", back_populates="events_participated")
    event = relationship("Event", back_populates="registrations")


# Association table for event hosts (many-to-many between users and events as hosts)
class EventHost(Base):
    __tablename__ = "event_hosts"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    event = relationship("Event", back_populates="hosts")
    user = relationship("User", back_populates="events_hosting")
