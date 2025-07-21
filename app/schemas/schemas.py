# Pydantic schemas for User, Event, and EventRegistration
import enum
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class UserRole(str, enum.Enum):
    attendee = "attendee"
    host = "host"

class EventBase(BaseModel):
    name: str
    date: datetime

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    host_id: int
    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class EventRegistrationBase(BaseModel):
    user_id: int
    event_id: int

class EventRegistrationCreate(EventRegistrationBase):
    pass

class EventRegistration(EventRegistrationBase):
    id: int
    class Config:
        orm_mode = True
