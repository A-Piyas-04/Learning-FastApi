# QuickContacts Backend Documentation

## Overview
- Stack: FastAPI + SQLModel + PostgreSQL/SQLite
- Entrypoint: `backend/main.py`
- Models: `backend/models.py`
- Database config/session: `backend/database.py`

## Models
- `ContactBase` fields: `name`, `phone`, `email`
- `Contact` table: adds `id`, `created_at`
- `ContactCreate`, `ContactRead`, `ContactUpdate` schemas
- Validation:
  - `name` trimmed, non-empty, max 100
  - `phone` at least 10 digits (separators allowed)
  - `email` validated via Pydantic `EmailStr`

## Database
- Env via `.env` (`POSTGRES_*`) or `DATABASE_URL`
- Default creates tables on startup
- Fallback to SQLite if Postgres fails
- Session provided to routes via dependency `get_session`

## API Endpoints
- Health: `GET /health`
- Contacts:
  - List: `GET /contacts`
    - Query: `skip`, `limit`, `name`, `email`, `phone`, `search`, `sort_by`, `sort_order`
  - Get one: `GET /contacts/{id}`
  - Create one: `POST /contacts`
  - Create batch: `POST /contacts/batch`
  - Update: `PUT /contacts/{id}` (partial)
  - Delete: `DELETE /contacts/{id}`

## Request/Response Examples
- Create one
```
POST /contacts
Content-Type: application/json
{
  "name": "John Doe",
  "phone": "+1 (555) 123-4567",
  "email": "john@example.com"
}
```
Response 201
```
{
  "id": 1,
  "name": "John Doe",
  "phone": "+1 (555) 123-4567",
  "email": "john@example.com",
  "created_at": "2025-01-01T00:00:00Z"
}
```

- Batch create
```
POST /contacts/batch
[
  { "name": "A", "email": "a@example.com", "phone": "5551234567" },
  { "name": "B", "email": "b@example.com", "phone": "5551234568" }
]
```

- List with filters/sort
```
GET /contacts?skip=0&limit=50&search=shakib&sort_by=created_at&sort_order=desc
```

## How API Connects to Models
- Dependency injection provides `Session` to each route (`get_session`) which is bound to the configured `engine`.
- Create:
  - Validates payload with `Contact.model_validate`
  - Adds instance to session, commits, and refreshes to get `id` and `created_at`.
- Read:
  - Uses `session.get(Contact, id)` for single
  - Uses `select(Contact)` with `where` clauses and `order_by` for lists
- Update:
  - Dumps provided fields with `model_dump(exclude_unset=True)`, applies to entity, commits
- Delete:
  - Deletes entity and commits

## Performance Notes
- Basic pagination and indexed sort fields recommended (`id`, `created_at`, `name`, `email`)
- Batch creation is atomic; if any item fails, transaction is rolled back

## Running
- Dev server: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- Frontend dev: `npm run dev` in `frontend/`

## Environment
- `.env` keys:
  - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`
  - `DATABASE_URL` overrides all (e.g., `postgresql://user:pass@host:5432/db` or `sqlite:///./app.db`)

