import time
from typing import List

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"


def test_create_contact_success(client):
    payload = {"name": "Alice", "email": "alice@example.com", "phone": "+1 (555) 000-0000"}
    r = client.post("/contacts", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Alice"
    assert "id" in data


def test_create_contact_validation_errors(client):
    # invalid email
    bad_email = {"name": "Bob", "email": "not-an-email", "phone": "5551234567"}
    r = client.post("/contacts", json=bad_email)
    assert r.status_code == 422

    # short phone
    bad_phone = {"name": "Bob", "email": "bob@example.com", "phone": "123"}
    r = client.post("/contacts", json=bad_phone)
    assert r.status_code == 422

    # empty name
    bad_name = {"name": " ", "email": "bob@example.com", "phone": "5551234567"}
    r = client.post("/contacts", json=bad_name)
    assert r.status_code == 422


def test_batch_creation_and_retrieval(client):
    batch = [
        {"name": "C1", "email": "c1@example.com", "phone": "5551234567"},
        {"name": "C2", "email": "c2@example.com", "phone": "5551234568"},
        {"name": "C3", "email": "c3@example.com", "phone": "5551234569"},
    ]
    r = client.post("/contacts/batch", json=batch)
    assert r.status_code == 201
    created: List[dict] = r.json()
    assert len(created) == 3

    # bulk fetch with pagination and sorting
    r = client.get("/contacts", params={"skip": 0, "limit": 10, "sort_by": "name", "sort_order": "asc"})
    assert r.status_code == 200
    listed = r.json()
    names = [c["name"] for c in listed]
    assert "C1" in names and "C2" in names and "C3" in names

    # filtering by email
    r = client.get("/contacts", params={"email": "c2@example.com"})
    assert r.status_code == 200
    filtered = r.json()
    assert len(filtered) >= 1
    assert any(c["email"] == "c2@example.com" for c in filtered)

    # single retrieval by ID
    c1_id = created[0]["id"]
    r = client.get(f"/contacts/{c1_id}")
    assert r.status_code == 200
    assert r.json()["id"] == c1_id


def test_edge_cases_empty_results(client):
    r = client.get("/contacts", params={"search": "no-such-name-xyz"})
    assert r.status_code == 200
    assert r.json() == []


def test_performance_bulk_operations(client):
    # measure batch creation of 200 contacts
    batch = [{"name": f"U{i}", "email": f"u{i}@example.com", "phone": f"555000{i:04d}"} for i in range(200)]
    t0 = time.perf_counter()
    r = client.post("/contacts/batch", json=batch)
    t1 = time.perf_counter()
    assert r.status_code == 201
    create_time = t1 - t0

    # measure retrieval with sorting and pagination
    t0 = time.perf_counter()
    r = client.get("/contacts", params={"skip": 0, "limit": 100, "sort_by": "created_at", "sort_order": "desc"})
    t1 = time.perf_counter()
    assert r.status_code == 200
    fetch_time = t1 - t0

    # basic performance thresholds (generous to reduce flakiness)
    assert create_time < 5.0
    assert fetch_time < 2.0

