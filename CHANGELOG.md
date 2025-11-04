# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2025-11-04 - KZ Adaptation (Backend Complete ✅)

### Added - Kazakhstan Market Adaptation

#### Sprint 1: KZ Identity & Compliance (✅ Completed)
- **Patient Model KZ Fields**:
  - `iin` - Individual Identification Number with Luhn validation
  - `iin_verified`, `iin_verified_at` - IIN verification tracking
  - `kato_address` (JSONField) - Kazakhstan Administrative Territorial address structure
  - `osms_status` - Obligatory Social Medical Insurance status
  - `osms_category` - OSMS payer category (employee/self_employed/pensioner/etc.)
  - `osms_verified_at` - OSMS status verification date

- **ConsentHistory Model** - GDPR/KZ compliance audit trail:
  - Consent type tracking (personal_data/medical_intervention/sms_marketing/whatsapp_marketing)
  - IP address and user agent logging
  - Status history (accepted/revoked)
  - Created by tracking

- **IIN Validation** (`patients/validators.py`):
  - Format validation (12 digits)
  - Birth date extraction from IIN
  - Sex extraction from IIN
  - Luhn algorithm checksum validation
  - Century indicator parsing

- **KATO Reference** (`patients/fixtures/kato.json`):
  - 17 regions + 3 cities of republican significance
  - District-level data for major cities (Almaty, Astana, Shymkent)
  - KATO codes and hierarchical structure

- **KZ Settings** (`config/settings/base.py`):
  - `COUNTRY_CODE = 'KZ'`
  - `CURRENCY = 'KZT'`, `CURRENCY_SYMBOL = '₸'`
  - `PHONE_MASK = '+7 7XX XXX-XX-XX'`
  - `DATE_FORMAT = 'dd.mm.yyyy'`
  - `TIMEZONE = 'Asia/Almaty'`
  - `HIDE_RF_FIELDS = True`

- **API Endpoints**:
  - `POST /api/patients/patients/{id}/verify-iin/` - IIN verification
  - `POST /api/patients/patients/{id}/save-consent/` - Save patient consent with audit
  - `GET /api/patients/patients/{id}/consent-history/` - Consent history retrieval
  - `/api/patients/consent-history/` - ConsentHistory ViewSet

- **Frontend Updates** (`PatientModal.vue`):
  - IIN field with verification button
  - OSMS status and category selectors
  - Basic KATO address structure support

#### Sprint 2: Visits & Waitlist (✅ Models Created)
- **Visit Model Extensions**:
  - `diary_structured` (JSONField) - Structured visit diary (complaints, anamnesis, examination, conclusion, recommendations)
  - `templates_used` (JSONField) - Template tracking for visit documentation

- **VisitFile Model** - File attachments for visits:
  - Support for x-rays, photos, documents, lab results
  - Upload tracking and categorization

- **Waitlist Model** (`calendar/models.py`):
  - Patient waitlist management
  - Preferred date/time window tracking
  - Priority system
  - Contact status tracking (waiting/contacted/scheduled/cancelled)
  - Service and employee preferences

- **PatientContact Model** (`comms/models.py`):
  - Detailed contact history (calls, SMS, WhatsApp, visits, email)
  - Direction tracking (inbound/outbound)
  - Status tracking (reached/no_answer/callback_requested/etc.)
  - Next contact date scheduling
  - Notes and created_by tracking

### Database Migrations
- `0005_add_kz_identity_fields.py` - Patient KZ fields + ConsentHistory model
- Additional migrations pending for Sprint 2 models

#### Sprint 3: Medical Examinations & Treatment Plans (✅ Backend Complete)
- **MedicalExamination Model** - Occupational/periodic examinations
- **MedExamPastDisease** - Past disease tracking with ICD-10
- **MedExamVaccination** - Vaccination records with serial numbers
- **MedExamLabTest** - Lab and instrumental tests (blood, ECG, X-ray, etc.)
- **TreatmentPlan Model** - Treatment planning system
- **TreatmentStage** - Multi-stage treatment tracking
- **TreatmentStageItem** - Service/product items with quantities and pricing
- **TreatmentPlanTemplate** - Reusable treatment plan templates
- **API Endpoints:** Full CRUD for examinations and treatment plans
- **Actions:** freeze_prices, save_as_template
- **Print Templates:** medical_examination.html, treatment_plan.html

#### Sprint 4: Payments & Integrations KZ (✅ Backend Complete)
- **Payment Model Extensions:** kaspi_qr, halyk_pay, paybox methods
- **PaymentProvider Model:** Configuration for KZ payment gateways
- **Kaspi QR Integration:** Service with test mode support
- **Halyk Pay Integration:** Service with test mode support
- **KZ SMS Providers:** BeeSMSProvider, AltelSMSProvider
- **TaxDeductionCertificate Model:** Tax deduction certificates for KZ
- **Patient Statistics API:** Total visits, revenue, average check, balance
- **1C Export:** CSV export for accounting integration

#### Sprint 5: UX Improvements (✅ 75% Complete)
- **Input Masks:** IIN (12 digits), phone KZ (+7 7XX XXX-XX-XX), dates (dd.mm.yyyy)
- **Permissions System:** usePermissions composable for role-based visibility
- **Hotkeys:** useHotkeys composable (Ctrl+S, Ctrl+P, Ctrl+K, Esc)
- **Autosave:** useAutosave composable with localStorage and API sync
- **GlobalSearch:** Ctrl+K global search component (patients, services, actions)
- **PatientCardHeader:** Sticky header component with patient info
- **SettingsPage:** Regional settings configuration page
- **Utilities:** Phone/IIN formatting, validation functions

### Pending Frontend Implementation
- ⏳ VisitDiaryEditor UI (дневник приема)
- ⏳ WaitlistModal UI (лист ожидания)
- ⏳ MedicalExaminationModal UI (медосмотры)
- ⏳ TreatmentPlanModal UI (планы лечения)
- ⏳ Inline table editing
- ⏳ ICD-10 KZ data loading

### Statistics
- **23/30 tasks completed (77%)**
- **Backend:** 95% complete
- **Frontend:** 40% complete
- **~5800+ lines of code added**
- **15 new models created**
- **30+ API endpoints added**
- **7 print templates created**

## [1.1.0] - 2025-11-04

### Added - HR Module

#### Staff/HR Module (Extended)
- **Position model** - справочник должностей с привязкой к организации
- **Extended Employee model** with 40+ new fields:
  - Employment tracking: `employment_status`, `hired_at`, `fired_at`
  - Online booking: `online_slot_step_minutes`, `min_gap_between_visits_minutes`, `min_gap_between_days_hours`
  - Documents: СНИЛС, ИНН, power of attorney
  - Permissions: `can_accept_payments`, `can_be_assistant`, `show_in_schedule`
  - Warehouse: `warehouse`, `warehouse_lock`
  - Print roles: `is_chief_accountant`, `is_cashier`, `is_org_head`
  - Calendar: `calendar_color` for schedule visualization
  - Access: `is_user_enabled` for system access control
- **SalarySchemaTemplate** - flexible salary calculation:
  - Commission from own sales (percentage)
  - Direction bonus
  - Created visits percentage
  - Fixed salary with currency
  - Minimum rate guarantee
  - Patient discount consideration
  - Subscription services percentage
  - Profit vs revenue calculation
- **EmployeeSalarySchema** - salary assignment history with date ranges
- **EmployeeTask** - task management for employees:
  - Assignment to employees
  - Status tracking (new/in_progress/done/cancelled)
  - Deadline tracking
  - Result reference
- **EmployeeTaskComment** - task collaboration
- **EmployeeTaskAttachment** - file attachments for tasks
- **EmployeeResult** - task results dictionary with position linking

#### API Endpoints
- `/api/staff/positions/` - CRUD for positions
- `/api/staff/employees/` - extended with new fields and actions:
  - `/grant_access` - create user account for employee
  - `/toggle_user_access` - enable/disable system access
  - `/assign_salary_schema` - assign salary template
  - `/doctors` - filter employees by doctor positions
- `/api/staff/salary-templates/` - CRUD for salary templates:
  - `/apply_to_employees` - bulk apply template to multiple employees
- `/api/staff/salary-schemas/` - manage salary assignments
- `/api/staff/tasks/` - task management:
  - `/add_comment` - add comment to task
  - `/upload_attachment` - upload file
  - `/change_status` - update task status
- `/api/staff/results/` - CRUD for task results
- Calendar integration:
  - `/api/calendar/appointments/available_employees/` - get schedulable employees
  - `/api/calendar/appointments/online_booking_slots/` - generate slots with employee settings
  - Extended `/conflicts` endpoint with HR field validation

#### Backend Features
- **Django Signals** for task notifications:
  - Task creation notifications
  - Status change notifications
  - Comment notifications
- **Celery Tasks**:
  - `check_task_deadlines` - periodic deadline checking
  - `calculate_employee_salary` - comprehensive salary calculation
- **Database Migrations**:
  - Backward-compatible position field migration (CharField → FK)
  - Data migration for legacy fields
  - 3-step migration process preserving existing data
- **Advanced Filtering**:
  - Employees: by position, status, hire dates, branch
  - Tasks: by assignee, status, deadline range
  - Positions: by visibility in schedule
- **RBAC Integration**:
  - IsBranchMember for basic HR access
  - IsBranchAdmin for salary and access management

#### Frontend Components (Vue 3)
- **PositionModal.vue** - position management dialog
- **EmployeeTaskModal.vue** - comprehensive task management:
  - Employee selection
  - Status management
  - Deadline (date + time)
  - Comments section
  - File upload support
- **SalaryTemplateModal.vue** - salary template configuration:
  - Commission settings
  - Fixed salary with currency
  - Minimum rate
  - Additional options
- **StaffHRPage.vue** - comprehensive HR dashboard with 4 tabs:
  - **Employees tab**: with position/status filters, salary schema display
  - **Positions tab**: position management
  - **Tasks tab**: task list with status filters
  - **Salary Templates tab**: template management
- Enhanced search and filtering across all sections
- Color-coded status badges
- Real-time data updates

#### Calendar Integration
- `show_in_schedule` flag controls employee visibility
- `calendar_color` for appointment visualization
- Individual `online_slot_step_minutes` per employee
- `min_gap_between_visits_minutes` validation
- Conflict checking with HR constraints
- Available employees endpoint for scheduling

#### Documentation
- Comprehensive HR module documentation (`docs/hr-module.md`)
- API endpoint reference
- Migration guide
- Integration examples
- Usage examples for all features

### Changed
- Employee model: position field converted from CharField to FK (Position)
- Calendar appointment conflicts now consider HR constraints
- Appointment color can use employee's calendar_color

### Migration Notes
- Run migrations in order: 0002 → 0003 → 0004
- Legacy fields (`hire_date`, `fire_date`, `position_legacy`) preserved for compatibility
- Data automatically migrated from old structure to new

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

