# API Reference - Desktop Dictation App

## Authentication

### Login
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "doctor1",
  "password": "password123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "doctor1",
    "full_name": "Иванов Иван Иванович",
    "role": "doctor"
  }
}
```

### Get Current User
```http
GET /api/v1/auth/me/
Authorization: Bearer <token>
```

## Consent System

### Search Patient by IIN
```http
POST /api/v1/consent/search-patient/
Authorization: Bearer <token>
Content-Type: application/json

{
  "iin": "123456789012"
}
```

**Response:**
```json
{
  "id": 123,
  "fio_masked": "Сидоров С***",
  "age": 35,
  "has_telegram": true,
  "iin_masked": "1234********"
}
```

### Create Access Request
```http
POST /api/v1/consent/access-requests/
Authorization: Bearer <token>
Content-Type: application/json

{
  "patient_iin": "123456789012",
  "scopes": ["read_records", "write_records"],
  "reason": "Прием у врача",
  "requested_duration_days": 1
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "patient": 123,
  "status": "pending",
  "delivery_channel": "telegram",
  "created_at": "2025-11-05T10:30:00Z",
  "expires_at": "2025-11-05T10:40:00Z"
}
```

### Poll Access Request Status
```http
GET /api/v1/consent/access-requests/{id}/status/
Authorization: Bearer <token>
```

**Response (pending):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "status_display": "Ожидает ответа",
  "created_at": "2025-11-05T10:30:00Z",
  "expires_at": "2025-11-05T10:40:00Z",
  "delivery_channel": "telegram"
}
```

**Response (approved):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "approved",
  "status_display": "Одобрено",
  "grant": {
    "grant_id": "660e8400-e29b-41d4-a716-446655440111",
    "valid_to": "2025-11-06T10:30:00Z",
    "scopes": ["read_records", "write_records"]
  },
  "patient_context": {
    "patient_id": 123,
    "full_name": "Сидоров Сидор Сидорович",
    "age": 35,
    "birth_date": "1988-05-15",
    "sex": "M",
    "iin_masked": "1234********",
    "osms_status": "insured",
    "appointment_id": 456,
    "visit_id": 789
  }
}
```

## Patient Data

### Get Patient by Grant
```http
GET /api/v1/patients/by-grant/{grant_id}/
Authorization: Bearer <token>
X-Access-Grant-ID: {grant_id}
```

**Response:**
```json
{
  "id": 123,
  "full_name": "Сидоров Сидор Сидорович",
  "first_name": "Сидор",
  "last_name": "Сидоров",
  "middle_name": "Сидорович",
  "birth_date": "1988-05-15",
  "age": 35,
  "sex": "M",
  "phone": "+77012345678",
  "iin_masked": "1234********",
  "osms_status": "insured"
}
```

## Visits

### Create Visit
```http
POST /api/v1/visits/visits/
Authorization: Bearer <token>
X-Access-Grant-ID: {grant_id}
Content-Type: application/json

{
  "appointment": 456,
  "status": "draft"
}
```

**Response:**
```json
{
  "id": 789,
  "appointment": 456,
  "patient_name": "Сидоров Сидор Сидорович",
  "status": "draft",
  "created_at": "2025-11-05T10:35:00Z"
}
```

### Save Visit Note (Dictation)
```http
POST /api/v1/visits/notes/
Authorization: Bearer <token>
X-Access-Grant-ID: {grant_id}
Content-Type: application/json

{
  "visit_id": 789,
  "raw_transcript": "Пациент жалуется на головную боль...",
  "structured_data": {
    "diagnosis": "ОРВИ",
    "recommendations": "Постельный режим, обильное питье"
  },
  "language": "ru",
  "audio_duration": 180,
  "metadata": {
    "created_via": "desktop_app",
    "timestamp": "2025-11-05T10:40:00Z"
  }
}
```

**Response:**
```json
{
  "id": 789,
  "status": "in_progress",
  "diary_structured": {
    "transcript": "Пациент жалуется на головную боль...",
    "language": "ru",
    "audio_duration": 180,
    "diagnosis": "ОРВИ",
    "recommendations": "Постельный режим, обильное питье",
    "last_updated": "2025-11-05T10:40:00Z",
    "updated_by": "Иванов Иван Иванович"
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "ИИН должен состоять из 12 цифр"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "error": "Grant has expired or is not yet valid",
  "grant_id": "660e8400-e29b-41d4-a716-446655440111",
  "valid_from": "2025-11-05T10:30:00Z",
  "valid_to": "2025-11-06T10:30:00Z"
}
```

### 404 Not Found
```json
{
  "error": "Пациент с таким ИИН не найден"
}
```

## Rate Limiting

- **Access Requests**: максимум 3 запроса в день на одного пациента от одной организации
- **OTP TTL**: 10 минут
- **Grant Duration**: настраивается, по умолчанию 2 часа для desktop

## Security Headers

### X-Access-Grant-ID
Требуется для всех запросов к данным пациента из внешней организации.

```http
X-Access-Grant-ID: 660e8400-e29b-41d4-a716-446655440111
```

### Response Headers

При использовании grant в ответе возвращаются дополнительные заголовки:

```http
X-Grant-Valid-Until: 2025-11-06T10:30:00Z
X-Grant-Scopes: read_records,write_records
```

## Audit Logging

Все действия с данными пациентов логируются автоматически:

- Кто (user, organization)
- Что (action: read/write/share/revoke)
- Когда (timestamp)
- Какой объект (Visit, Patient, EHR Record)
- Через какой grant (если применимо)
- IP и User-Agent

Audit logs доступны через:

```http
GET /api/v1/consent/audit-logs/
Authorization: Bearer <token>
```

