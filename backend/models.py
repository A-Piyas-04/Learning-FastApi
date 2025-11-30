"""Contact models for ORM and Pydantic serialization.

Defines the Contact table model and related schemas for CRUD operations.
"""
# models.py
# (1) Contact model used for ORM and Pydantic serialization.

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import EmailStr, field_validator
import re

class ContactBase(SQLModel):
    """Base model for Contact with common fields shared across schemas."""
    name: str = Field(min_length=1, max_length=100, description="Contact's full name")
    phone: str = Field(min_length=10, max_length=20, description="Contact's phone number")
    email: EmailStr = Field(description="Contact's email address")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format - allows digits, spaces, hyphens, parentheses, and plus sign."""
        # Remove spaces and common separators for validation
        cleaned = re.sub(r'[\s\-\(\)\+]', '', v)
        if not cleaned.isdigit():
            raise ValueError('Phone number must contain only digits, spaces, hyphens, parentheses, and plus sign')
        if len(cleaned) < 10:
            raise ValueError('Phone number must have at least 10 digits')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip()

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
