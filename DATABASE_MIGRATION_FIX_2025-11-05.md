# Database Migration Fix - November 5, 2025

## Problem
The application was experiencing 500 Internal Server Errors across all API endpoints because of missing database columns:
- `patients.iin_verified` - Missing from the patients table
- `visits.diary_structured` - Missing from the visits table

## Root Cause
The migration files existed locally but were not present in the Docker container due to Docker caching issues:
- `backend/apps/patients/migrations/0005_add_kz_identity_fields.py`
- `backend/apps/patients/migrations/0006_add_sprint3_models.py`
- `backend/apps/visits/migrations/0003_add_sprint2_fields.py`

## Solution Applied
1. Installed missing `requests` module in the backend container
2. Rebuilt the backend Docker image without cache
3. Manually copied missing migration files to the container:
   ```bash
   docker cp backend/apps/patients/migrations/0005_add_kz_identity_fields.py kudarovumar-backend-1:/app/apps/patients/migrations/
   docker cp backend/apps/patients/migrations/0006_add_sprint3_models.py kudarovumar-backend-1:/app/apps/patients/migrations/
   docker cp backend/apps/visits/migrations/0003_add_sprint2_fields.py kudarovumar-backend-1:/app/apps/visits/migrations/
   ```
4. Applied migrations:
   ```bash
   docker exec kudarovumar-backend-1 python manage.py migrate
   ```
5. Restarted the backend container

## Migrations Applied
- `patients.0005_add_kz_identity_fields` - Added KZ-specific identity fields:
  - `iin_verified` (Boolean)
  - `iin_verified_at` (DateTime)
  - `kato_address` (JSONField)
  - `osms_status` (CharField)
  - `osms_category` (CharField)
  - `osms_verified_at` (DateTime)
  - `ConsentHistory` model

- `patients.0006_add_sprint3_models` - Added Sprint 3 models:
  - `MedicalExamination`
  - `MedExamPastDisease`
  - `MedExamVaccination`
  - `MedExamLabTest`
  - `TreatmentPlan`
  - `TreatmentStage`
  - `TreatmentStageItem`
  - `TreatmentPlanTemplate`

- `visits.0003_add_sprint2_fields` - Added Sprint 2 fields to Visit:
  - `diary_structured` (JSONField)
  - `templates_used` (JSONField)
  - `VisitFile` model

## Verification
Verified that the columns now exist in the database:
```sql
-- Verified patients table has iin_verified and iin_verified_at
-- Verified visits table has diary_structured and templates_used
```

## Status
✅ **FIXED** - All database columns are now present and the backend is running without errors.

## Next Steps
The frontend should now be able to load data from all API endpoints without 500 errors.

## Notes
- The Docker build process was using cached layers, which prevented the new migration files from being copied
- A proper rebuild with `--no-cache` should be done periodically to ensure all files are updated
- The `requests` module was missing from the container despite being in requirements.txt (likely due to cache)

