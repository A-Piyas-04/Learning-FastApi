# QuickContacts API

Base URL: `http://localhost:8000`

## Health
- `GET /health`
- Response:
```json
{ "status": "healthy", "service": "QuickContacts API", "version": "1.0.0" }
```

## Contacts

### Create
- `POST /contacts`
- Request:
```json
{ "name": "John Doe", "email": "john@example.com", "phone": "+1 (555) 123-4567" }
```
- Response `201`:
```json
{ "id": 1, "name": "John Doe", "email": "john@example.com", "phone": "+1 (555) 123-4567", "created_at": "2025-01-01T00:00:00Z" }
```

### Batch Create
- `POST /contacts/batch`
- Request:
```json
[
  { "name": "A", "email": "a@example.com", "phone": "5551234567" },
  { "name": "B", "email": "b@example.com", "phone": "5551234568" }
]
```
- Response `201`:
```json
[
  { "id": 10, "name": "A", "email": "a@example.com", "phone": "5551234567", "created_at": "..." },
  { "id": 11, "name": "B", "email": "b@example.com", "phone": "5551234568", "created_at": "..." }
]
```

### Retrieve List
- `GET /contacts`
- Query params:
  - `skip` (int, default 0)
  - `limit` (int, default 100)
  - `name` (string contains)
  - `email` (string contains)
  - `phone` (string contains)
  - `search` (string contains across name/email/phone)
  - `sort_by` (`created_at|name|email|id`, default `created_at`)
  - `sort_order` (`asc|desc`, default `desc`)
- Response `200`: `Contact[]`

### Retrieve One
- `GET /contacts/{id}`
- Response `200`: `Contact`
- Errors:
```json
{ "detail": "Contact with ID {id} not found" }
```

### Update
- `PUT /contacts/{id}`
- Request (partial allowed):
```json
{ "name": "New Name" }
```
- Response `200`: `Contact`

### Delete
- `DELETE /contacts/{id}`
- Response `204`

## Validation
- `name`: non-empty, max 100
- `phone`: min 10 digits (separators allowed)
- `email`: RFC format

