# main.py
# Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000

from typing import List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select

from database import create_db_and_tables, get_session
from models import Contact, ContactCreate, ContactRead, ContactUpdate


app = FastAPI(title="QuickContacts API")

# Allow React dev server origin (adjust port if needed)
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:3000",  # CRA default, if used
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # Ensure DB tables exist when the app starts
    create_db_and_tables()

# --- Endpoints ---

@app.get("/contacts", response_model=List[ContactRead])
def list_contacts(session=Depends(get_session)):
    """List all contacts"""
    contacts = session.exec(select(Contact).order_by(Contact.created_at.desc())).all()
    return contacts


@app.get("/contacts/{contact_id}", response_model=ContactRead)
def get_contact(contact_id: int, session=Depends(get_session)):
    """Get contact by id"""
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact



@app.post("/contacts", response_model=ContactRead, status_code=201)
def create_contact(contact_in: ContactCreate, session=Depends(get_session)):
    """Create a contact"""
    contact = Contact.from_orm(contact_in)
    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact

@app.put("/contacts/{contact_id}", response_model=ContactRead)
def update_contact(contact_id: int, contact_in: ContactUpdate, session=Depends(get_session)):
    """Update contact fields (partial allowed)"""
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    contact_data = contact_in.dict(exclude_unset=True)
    for key, value in contact_data.items():
        setattr(contact, key, value)
    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact

@app.delete("/contacts/{contact_id}", status_code=204)
def delete_contact(contact_id: int, session=Depends(get_session)):
    """Delete a contact"""
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    session.delete(contact)
    session.commit()
    return None
