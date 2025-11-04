# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-11-04

### Added - MVP Release

#### Infrastructure
- Django 5 backend with modular architecture
- Vue 3 + Vite frontend with Naive UI
- Docker Compose setup with PostgreSQL, Redis, MinIO
- Celery for background tasks
- Django Channels for WebSocket
- Makefile for common commands

#### Core Module
- JWT authentication with refresh tokens
- 2FA TOTP implementation
- Multi-tenant middleware (X-Branch-Id)
- RBAC system with 8 roles
- Object-level permissions

#### Organization Module
- Organization and Branch models
- Room and Resource management
- Flexible Settings model (key-value)
- ClinicInfo model for legal details
- Full CRUD API

#### Staff Module
- Employee model with full employment data
- Employee-Branch many-to-many assignments
- Employee-Service assignments with custom pricing
- Grant system access endpoint
- Commission tracking

#### Patients Module
- Patient model with medical/financial data
- Phone/IIN deduplication
- Representative model for guardians
- PatientFile model for documents
- Search by phone/IIN endpoint
- Balance management

#### Services Module
- Hierarchical category tree
- Service model with pricing and materials
- PriceList for time-based pricing
- ICD-10 codes (МКБ-10)
- ServiceMaterial for tracking consumption

#### Calendar Module
- Availability (schedule templates)
- Appointment model with conflict detection
- WebSocket real-time updates
- Drag & drop support
- Status management
- Resource allocation

#### Visits Module
- Visit model based on appointments
- VisitService with ICD codes
- VisitPrescription for medications
- VisitResource tracking
- Mark arrived functionality

#### Billing Module
- Invoice generation
- Multiple payment methods (cash, card, kaspi, cloud)
- CashShift management
- Payment tracking

#### Warehouse Module
- Stock items and batches
- Lot and expiration tracking
- Stock moves (in/out/transfer)
- Visit reference for automatic deduction

#### Communications Module
- Template management (SMS/Email/WhatsApp/Telegram)
- MessageLog for tracking
- Mock SMS provider for development
- Celery tasks for appointment reminders
- Manual send endpoint

#### Reports Module
- Appointments report
- Revenue report
- SMS balance report
- Excel export functionality

#### Frontend
- Vue 3 with Composition API
- Pinia for state management
- Vue Router with auth guards
- Login page
- Main layout with sidebar menu
- Design system with tokens
- Status badges
- Data table component
- Modal wrapper
- Settings clinic page

#### Testing
- Pytest configuration
- Backend tests (auth, patients, services, appointments)
- Playwright E2E tests (auth, navigation)
- Test fixtures and conftest

#### Documentation
- Comprehensive README
- Deployment guide
- API documentation
- Architecture overview

#### Seed Data
- Management commands for initial data
- Test organization with 2 branches
- 3 employees (doctors)
- 10 test patients
- 24 services across 6 categories

### Features
- 🔐 Secure authentication with 2FA
- 🏢 Multi-tenant support
- 📅 Real-time calendar updates
- 👥 Patient management with deduplication
- 🦷 Service catalog with categories
- 💰 Billing and invoicing
- 📦 Warehouse management
- 📧 Automated notifications
- 📊 Reports and analytics
- 🌐 API documentation with Swagger

