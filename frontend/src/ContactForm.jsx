import React, { useState, useEffect } from "react";

export default function ContactForm({ onCreate, editing, onUpdate, contacts = [] }) {
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [knownNumber, setKnownNumber] = useState("");

  useEffect(() => {
    if (editing) {
      setName(editing.name);
      setPhone(editing.phone);
      setEmail(editing.email);
    } else {
      setName(""); setPhone(""); setEmail("");
    }
  }, [editing]);

  useEffect(() => {
    const n = name.trim().toLowerCase();
    if (!n) { setKnownNumber(""); return; }
    const match = contacts.find(c => c.name.toLowerCase() === n);
    setKnownNumber(match ? match.phone : "");
  }, [name, contacts]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = { name, phone, email };
    if (editing && onUpdate) {
      onUpdate(editing.id, payload);
    } else {
      onCreate(payload);
      setName(""); setPhone(""); setEmail("");
    }
  };

  return (
    <form className="form" onSubmit={handleSubmit}>
      <input placeholder="Name" value={name} onChange={e => setName(e.target.value)} required />
      <input placeholder="Phone" value={phone} onChange={e => setPhone(e.target.value)} required />
      <input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
      <button type="submit">{editing ? "Update" : "Add"}</button>
      {editing && <small>Editing contact ID {editing.id}</small>}
      {knownNumber && <small className="muted">Known number for this name: {knownNumber}</small>}
    </form>
  );
}
