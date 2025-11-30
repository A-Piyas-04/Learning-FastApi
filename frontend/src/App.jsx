import React, { useEffect, useState } from "react";
import ContactList from "./ContactList.jsx";
import ContactForm from "./ContactForm.jsx";

const API = "http://localhost:8000";

export default function App() {
  const [contacts, setContacts] = useState([]);
  const [editing, setEditing] = useState(null);
  const [message, setMessage] = useState("");
  const [search, setSearch] = useState("");
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [filterName, setFilterName] = useState("");
  const [filterEmail, setFilterEmail] = useState("");
  const [filterPhone, setFilterPhone] = useState("");
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");

  const fetchContacts = async () => {
    try {
      const params = new URLSearchParams();
      params.set("skip", "0");
      params.set("limit", "100");
      params.set("sort_by", sortBy);
      params.set("sort_order", sortOrder);
      if (search) params.set("search", search);
      if (filterName) params.set("name", filterName);
      if (filterEmail) params.set("email", filterEmail);
      if (filterPhone) params.set("phone", filterPhone);
      const res = await fetch(`${API}/contacts?${params.toString()}`);
      const data = await res.json();
      setContacts(data);
    } catch {
      setMessage("Failed to load contacts");
    }
  };

  useEffect(() => { fetchContacts(); }, []);
  useEffect(() => {
    const t = setTimeout(() => { fetchContacts(); }, 250);
    return () => clearTimeout(t);
  }, [search, filterName, filterEmail, filterPhone, sortBy, sortOrder]);

  const onCreate = async (contact) => {
    try {
      const res = await fetch(`${API}/contacts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(contact)
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      setContacts([data, ...contacts]);
      setMessage("Contact added");
    } catch {
      setMessage("Failed to add contact");
    }
  };

  const onUpdate = async (id, updates) => {
    try {
      const res = await fetch(`${API}/contacts/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates)
      });
      if (!res.ok) throw new Error();
      const updated = await res.json();
      setContacts(contacts.map(c => c.id === id ? updated : c));
      setEditing(null);
      setMessage("Contact updated");
    } catch {
      setMessage("Update failed");
    }
  };

  const onDelete = async (id) => {
    if (!confirm("Delete this contact?")) return;
    try {
      const res = await fetch(`${API}/contacts/${id}`, { method: "DELETE" });
      if (res.status === 204) {
        setContacts(contacts.filter(c => c.id !== id));
        setMessage("Contact deleted");
      } else {
        setMessage("Delete failed");
      }
    } catch {
      setMessage("Delete error");
    }
  };

  return (
    <div className="container">
      <h1>QuickContacts</h1>
      <div className="toolbar">
        <input
          className="search"
          placeholder="Search name, email, phone"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <button className="secondary" onClick={() => setFiltersOpen(!filtersOpen)}>
          {filtersOpen ? "Hide Filters" : "Advanced Filters"}
        </button>
      </div>
      {filtersOpen && (
        <div className="filters">
          <input placeholder="Name contains" value={filterName} onChange={e => setFilterName(e.target.value)} />
          <input placeholder="Email contains" value={filterEmail} onChange={e => setFilterEmail(e.target.value)} />
          <input placeholder="Phone contains" value={filterPhone} onChange={e => setFilterPhone(e.target.value)} />
          <select value={sortBy} onChange={e => setSortBy(e.target.value)}>
            <option value="created_at">Sort by Created</option>
            <option value="name">Sort by Name</option>
            <option value="email">Sort by Email</option>
            <option value="id">Sort by ID</option>
          </select>
          <select value={sortOrder} onChange={e => setSortOrder(e.target.value)}>
            <option value="asc">Asc</option>
            <option value="desc">Desc</option>
          </select>
        </div>
      )}
      <ContactForm onCreate={onCreate} editing={editing} onUpdate={onUpdate} contacts={contacts} />
      {message && <div className="message">{message}</div>}
      <ContactList contacts={contacts} onEdit={setEditing} onDelete={onDelete} />
    </div>
  );
}
