# API Documentation

## Base URL
`http://localhost:8000/api/v1`

## Authentication
All endpoints (except login) require JWT authentication.

### Headers
```
Authorization: Bearer <access_token>
X-Branch-Id: <branch_id>  (for multi-tenant operations)
```

## Endpoints

### Authentication

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123",
  "totp_token": "123456"  // if 2FA enabled
}

Response:
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": { ... },
  "branches": [ ... ]
}
```

#### Refresh Token
```http
POST /auth/refresh
{
  "refresh": "jwt_refresh_token"
}
```

#### Get Current User
```http
GET /auth/me
```

### Organization

#### List Branches
```http
GET /org/branches
```

#### Get Clinic Info
```http
GET /org/clinic-info
```

#### Update Clinic Info
```http
PATCH /org/clinic-info
{
  "inn": "1234567890",
  "kpp": "123456789",
  ...
}
```

### Staff

#### List Employees
```http
GET /staff/employees?branch=1&is_active=true
```

#### Create Employee
```http
POST /staff/employees
{
  "organization": 1,
  "first_name": "Иван",
  "last_name": "Иванов",
  "position": "Врач-стоматолог",
  "phone": "+77011234567",
  "hire_date": "2024-01-01",
  "color": "#2196F3"
}
```

#### Grant System Access
```http
POST /staff/employees/{id}/grant_access
{
  "password": "secure_password",
  "role": "doctor"
}
```

### Patients

#### Search Patient
```http
POST /patients/patients/search
{
  "phone": "+77011234567"
}

Response:
{
  "found": true,
  "count": 1,
  "patients": [ ... ]
}
```

#### Create Patient
```http
POST /patients/patients
{
  "organization": 1,
  "first_name": "Асель",
  "last_name": "Нұрланова",
  "birth_date": "1990-05-15",
  "sex": "F",
  "phone": "+77011234567"
}
```

### Services

#### List Services
```http
GET /services/services?category=1&is_active=true&search=лечение
```

#### Get Category Tree
```http
GET /services/categories/tree
```

### Calendar

#### List Appointments
```http
GET /calendar/appointments?branch=1&date_from=2024-01-01&date_to=2024-01-31
```

#### Create Appointment
```http
POST /calendar/appointments
{
  "branch": 1,
  "employee": 1,
  "patient": 1,
  "start_datetime": "2024-01-15T10:00:00Z",
  "end_datetime": "2024-01-15T11:00:00Z",
  "status": "booked",
  "is_primary": true
}
```

#### Move Appointment (Drag & Drop)
```http
POST /calendar/appointments/{id}/move
{
  "start_datetime": "2024-01-15T14:00:00Z",
  "end_datetime": "2024-01-15T15:00:00Z"
}
```

#### Check Conflicts
```http
GET /calendar/appointments/conflicts?employee=1&start_datetime=...&end_datetime=...
```

### WebSocket

#### Calendar Real-time Updates
```javascript
ws://localhost:8001/ws/calendar/1  // branch_id = 1

// Incoming events:
{
  "type": "appointment_created",
  "appointment": { ... }
}

{
  "type": "appointment_updated",
  "appointment": { ... }
}

{
  "type": "appointment_moved",
  "appointment": { ... }
}
```

### Visits

#### Create Visit
```http
POST /visits/visits
{
  "appointment": 1,
  "status": "in_progress"
}
```

#### Mark Patient Arrived
```http
POST /visits/visits/{id}/mark_arrived
```

### Billing

#### Create Invoice
```http
POST /billing/invoices
{
  "visit": 1,
  "amount": 50000
}
```

#### Create Payment
```http
POST /billing/payments
{
  "invoice": 1,
  "method": "cash",
  "amount": 50000
}
```

### Reports

#### Appointments Report
```http
GET /reports/appointments?date_from=2024-01-01&date_to=2024-01-31
```

#### Export to Excel
```http
GET /reports/export?type=appointments
```

## Error Responses

```json
{
  "error": "Error message",
  "details": { ... }
}
```

## Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

