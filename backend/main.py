"""QuickContacts API - FastAPI backend for managing contacts.

Provides RESTful endpoints for CRUD operations on contacts with PostgreSQL.
Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
# main.py
# Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000

from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select, Session
from sqlalchemy import or_

from database import create_db_and_tables, get_session
from models import Contact, ContactCreate, ContactRead, ContactUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Initialize database tables
    create_db_and_tables()
    yield
    # Shutdown: cleanup if needed (currently none)


app = FastAPI(
    title="QuickContacts API",
    description="A modern contact management REST API with PostgreSQL",
    version="1.0.0",
    lifespan=lifespan
)

# Allow React dev server origin (adjust port if needed)
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:3000",  # CRA default, if used
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health Check ---

@app.get("/health", tags=["Health"])
def health_check():
    """Check API health status."""
    return {
        "status": "healthy",
        "service": "QuickContacts API",
        "version": "1.0.0"
    }

# --- Contact Endpoints ---

@app.get("/contacts", response_model=List[ContactRead], tags=["Contacts"])
def list_contacts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    name: Optional[str] = Query(None, description="Filter by name (contains)"),
    email: Optional[str] = Query(None, description="Filter by email (contains)"),
    phone: Optional[str] = Query(None, description="Filter by phone (contains)"),
    search: Optional[str] = Query(None, description="Search across name, email, phone"),
    sort_by: str = Query("created_at", description="Sort field: created_at|name|email|id"),
    sort_order: str = Query("desc", description="Sort order: asc|desc"),
    session: Session = Depends(get_session)
):
    """List contacts with pagination, filtering, and sorting."""
    query = select(Contact)

    if name:
        query = query.where(Contact.name.ilike(f"%{name}%"))
    if email:
        query = query.where(Contact.email.ilike(f"%{email}%"))
    if phone:
        query = query.where(Contact.phone.ilike(f"%{phone}%"))
    if search:
        q = f"%{search}%"
        query = query.where(or_(
            Contact.name.ilike(q),
            Contact.email.ilike(q),
            Contact.phone.ilike(q)
        ))

    sort_field_map = {
        "created_at": Contact.created_at,
        "name": Contact.name,
        "email": Contact.email,
        "id": Contact.id,
    }
    sort_col = sort_field_map.get(sort_by, Contact.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    query = query.offset(skip).limit(limit)
    contacts = session.exec(query).all()
    return contacts


@app.get("/contacts/{contact_id}", response_model=ContactRead, tags=["Contacts"])
def get_contact(contact_id: int, session: Session = Depends(get_session)):
    """Get a specific contact by ID.
    
    Args:
        contact_id: The ID of the contact to retrieve
        session: Database session
        
    Returns:
        The requested contact
        
    Raises:
        HTTPException: 404 if contact not found
    """
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact with ID {contact_id} not found")
    return contact


@app.post("/contacts", response_model=ContactRead, status_code=201, tags=["Contacts"])
def create_contact(contact_in: ContactCreate, session: Session = Depends(get_session)):
    """Create a new contact.
    
    Args:
        contact_in: Contact data to create
        session: Database session
        
    Returns:
        The created contact with generated ID and timestamp
    """
    # Use model_validate instead of deprecated from_orm
    contact = Contact.model_validate(contact_in)
    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact


@app.post("/contacts/batch", response_model=List[ContactRead], status_code=201, tags=["Contacts"])
def create_contacts_batch(contacts_in: List[ContactCreate], session: Session = Depends(get_session)):
    """Create multiple contacts in a single request (atomic)."""
    contacts: List[Contact] = []
    for payload in contacts_in:
        contacts.append(Contact.model_validate(payload))
    try:
        for c in contacts:
            session.add(c)
        session.commit()
        for c in contacts:
            session.refresh(c)
        return contacts
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Batch creation failed: {e}")


@app.put("/contacts/{contact_id}", response_model=ContactRead, tags=["Contacts"])
def update_contact(
    contact_id: int,
    contact_in: ContactUpdate,
    session: Session = Depends(get_session)
):
    """Update a contact (partial update supported).
    
    Args:
        contact_id: The ID of the contact to update
        contact_in: Contact data to update (only provided fields will be updated)
        session: Database session
        
    Returns:
        The updated contact
        
    Raises:
        HTTPException: 404 if contact not found
    """
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact with ID {contact_id} not found")
    
    # Use model_dump instead of deprecated dict()
    contact_data = contact_in.model_dump(exclude_unset=True)
    for key, value in contact_data.items():
        setattr(contact, key, value)
    
    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact


@app.delete("/contacts/{contact_id}", status_code=204, tags=["Contacts"])
def delete_contact(contact_id: int, session: Session = Depends(get_session)):
    """Delete a contact.
    
    Args:
        contact_id: The ID of the contact to delete
        session: Database session
        
    Returns:
        None (204 No Content)
        
    Raises:
        HTTPException: 404 if contact not found
    """
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact with ID {contact_id} not found")
    
    session.delete(contact)
    session.commit()
    return None
