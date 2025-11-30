import React from "react";

export default function ContactList({ contacts, onEdit, onDelete }) {
  if (!contacts.length) return <div>No contacts yet.</div>;

  return (
    <div className="list">
      {contacts.map(c => (
        <div key={c.id} className="card">
          <div className="card-left">
            <strong>{c.name}</strong>
            <div>{c.phone}</div>
            <div className="muted">{c.email}</div>
            <div className="muted">Created: {new Date(c.created_at).toLocaleString()}</div>
          </div>
          <div className="card-actions">
            <button onClick={() => onEdit(c)}>Edit</button>
            <button onClick={() => onDelete(c.id)}>Delete</button>
          </div>
        </div>
      ))}
    </div>
  );
}
