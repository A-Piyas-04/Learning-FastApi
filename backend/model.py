# models.py
# (1) Contact model used for ORM and Pydantic serialization.

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class ContactBase(SQLModel):
    name: str
    phone: str
    email: str

class Contact(ContactBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)  # set creation time

class ContactCreate(ContactBase):
    pass

class ContactRead(ContactBase):
    id: int
    created_at: datetime

class ContactUpdate(SQLModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
