# Architecture Overview

## System Architecture

```
┌─────────────┐
│   Browser   │
│  (Vue 3)    │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────────────────────────┐
│         Nginx (Reverse Proxy)       │
└──────┬────────────────────┬─────────┘
       │                    │
       │ HTTP               │ WebSocket
       ▼                    ▼
┌─────────────┐      ┌──────────────┐
│   Django    │      │   Channels   │
│   (DRF)     │      │  (WebSocket) │
└──────┬──────┘      └──────┬───────┘
       │                    │
       │                    │
       ▼                    ▼
┌─────────────────────────────────────┐
│            PostgreSQL 16             │
└──────────────────────────────────────┘
       ▲
       │
┌──────┴──────┐
│    Redis    │
│  (Cache &   │
│   Celery)   │
└─────────────┘
       ▲
       │
┌──────┴──────┐
│   Celery    │
│   Workers   │
│  + Beat     │
└─────────────┘
```

## Multi-Tenant Architecture

```
Organization
    ├── Branch 1
    │   ├── Employees
    │   ├── Rooms
    │   ├── Resources
    │   └── Appointments
    └── Branch 2
        ├── Employees
        ├── Rooms
        └── ...
```

## Data Flow

### Creating an Appointment

1. User creates appointment in Calendar UI
2. Frontend sends POST to `/api/v1/calendar/appointments`
3. Backend validates (no conflicts)
4. Appointment saved to DB
5. WebSocket event sent to all connected clients
6. Calendar UI updates in real-time

### Visit Flow

1. Patient arrives → Mark as arrived
2. Doctor starts visit → Status: in_progress
3. Add services → Calculate total
4. Complete visit → Create invoice
5. Payment → Update invoice status
6. SMS receipt sent to patient

## Security Layers

### 1. Authentication
- JWT tokens (access + refresh)
- 2FA TOTP for staff
- Password validation

### 2. Authorization
- Role-based access control (RBAC)
- Object-level permissions
- Branch-scoped access

### 3. Multi-tenancy
- Organization isolation
- Branch-level access control
- X-Branch-Id header validation

## Database Schema

See ERD in main documentation.

Key relationships:
- Organization → Branches → Employees/Patients
- Appointment → Visit → Invoice → Payment
- Service → VisitService → Materials

## Real-time Updates

WebSocket channels for:
- Calendar appointments
- Future: notifications, chat

## Background Tasks

Celery tasks:
- Appointment reminders (24h, 3h, 1h before)
- Report generation
- Bulk SMS campaigns
- Data cleanup

## File Storage

- Development: Local filesystem
- Production: S3/MinIO for media files

## Caching Strategy

Redis cache for:
- User sessions
- Frequently accessed data
- WebSocket channel layers

## API Versioning

Current: `/api/v1/`
Future versions: `/api/v2/` with backward compatibility

