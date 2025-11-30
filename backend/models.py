"""Contact models for ORM and Pydantic serialization.

Defines the Contact table model and related schemas for CRUD operations.
"""
# models.py
# (1) Contact model used for ORM and Pydantic serialization.

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class ContactBase(SQLModel):
    """Base model for Contact with common fields shared across schemas."""
    name: str
    phone: str
    email: str

class Contact(ContactBase, table=True):
    """Contact table model with auto-generated ID and timestamp."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)  # set creation time

class ContactCreate(ContactBase):
    """Schema for creating a new contact (excludes id and created_at)."""

class ContactRead(ContactBase):
    """Schema for reading a contact (includes id and created_at)."""
    id: int
    created_at: datetime

class ContactUpdate(SQLModel):
    """Schema for updating a contact (all fields optional for partial updates)."""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
