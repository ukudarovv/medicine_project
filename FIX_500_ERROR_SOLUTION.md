# 500 Error Fix - Database Migration Issue

## Problem Diagnosis

Your frontend is receiving **500 Internal Server Error** on all API endpoints because:

1. **Docker Desktop is NOT running** - The backend, database, and Redis containers are not started
2. **Database migrations are not applied** - The database is missing the column `iin_verified` and other fields
3. **Local services are blocking ports** - Redis was running locally on port 6379 (now stopped)

## Error Details

From the Django logs:
```
psycopg2.errors.UndefinedColumn: column patients.iin_verified does not exist
LINE 1: ...."email", "patients"."address", "patients"."iin", "patients"...
```

This field is defined in migration `0005_add_kz_identity_fields.py` but the migration was never applied to the database.

## Solution Steps

### Step 1: Start Docker Desktop

1. **Open Docker Desktop** application on Windows
2. Wait for Docker to fully start (the whale icon in system tray should be steady, not animating)
3. Verify Docker is running:
   ```powershell
   docker ps
   ```
   Should show container list (even if empty), not an error

### Step 2: Start All Services

Once Docker is running:

```powershell
# Navigate to project root
cd "C:\Users\Kudarov Umar\Desktop\My Projects\Medicine"

# Start all containers
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Redis (port 6379)
- MinIO (ports 9000, 9001)
- Backend Django (port 8000)
- Channels/WebSocket (port 8001)
- Frontend Vue.js (port 5173)
- Celery Worker
- Celery Beat

### Step 3: Apply Database Migrations

```powershell
# Run migrations inside the backend container
docker-compose exec backend python manage.py migrate
```

This will apply all missing migrations including:
- `0005_add_kz_identity_fields.py` (adds iin_verified, kato_address, osms_status, etc.)
- `0006_add_sprint3_models.py` (adds medical examinations, treatment plans)

### Step 4: Verify Everything Works

1. **Check backend logs:**
   ```powershell
   docker-compose logs backend -f
   ```
   Look for errors (Ctrl+C to exit)

2. **Check if API is responding:**
   Open browser: http://localhost:8000/api/v1/

3. **Check frontend:**
   Open browser: http://localhost:5173/
   
   All pages should now load without 500 errors

### Step 5: Create Superuser (if needed)

If you need admin access:

```powershell
docker-compose exec backend python manage.py createsuperuser
```

## Troubleshooting

### If Docker won't start containers

Check if ports are already in use:

```powershell
# Check PostgreSQL port
netstat -ano | findstr :5432

# Check Redis port
netstat -ano | findstr :6379

# Check Backend port
netstat -ano | findstr :8000
```

If any ports are occupied, stop those processes:

```powershell
taskkill /PID <PID_NUMBER> /F
```

### If migrations fail

Check the database container is running:

```powershell
docker-compose ps db
```

View database logs:

```powershell
docker-compose logs db
```

### If still getting 500 errors

1. Restart all containers:
   ```powershell
   docker-compose down
   docker-compose up -d
   ```

2. Check for any other migration issues:
   ```powershell
   docker-compose exec backend python manage.py showmigrations
   ```

3. View detailed backend logs:
   ```powershell
   docker-compose exec backend tail -f /app/logs/django.log
   ```

## Quick Start Script

Save this as `start_project.ps1`:

```powershell
# Start Docker Desktop (you must do this manually first!)
Write-Host "Make sure Docker Desktop is running..." -ForegroundColor Yellow
Read-Host "Press Enter when Docker is ready"

# Navigate to project
Set-Location "C:\Users\Kudarov Umar\Desktop\My Projects\Medicine"

# Start containers
Write-Host "Starting containers..." -ForegroundColor Green
docker-compose up -d

# Wait for database to be ready
Write-Host "Waiting for database..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Apply migrations
Write-Host "Applying migrations..." -ForegroundColor Green
docker-compose exec backend python manage.py migrate

# Show status
Write-Host "`nContainers status:" -ForegroundColor Green
docker-compose ps

Write-Host "`nProject is ready!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000/api/v1/" -ForegroundColor Cyan
Write-Host "Admin Panel: http://localhost:8000/admin/" -ForegroundColor Cyan
```

Run it:
```powershell
powershell -ExecutionPolicy Bypass -File start_project.ps1
```

## Summary

The core issue is that **Docker Desktop must be running** for the application to work. Once Docker is running and migrations are applied, all 500 errors will be resolved.

**Current Status:**
- ✅ Redis local service stopped (port 6379 freed)
- ❌ Docker Desktop not running
- ❌ Database migrations not applied
- ❌ Application not running

**Next Action:**
1. Start Docker Desktop
2. Run `docker-compose up -d`
3. Run `docker-compose exec backend python manage.py migrate`
4. Access http://localhost:5173

---

**Created:** November 5, 2025
**Issue:** Database migration not applied - `iin_verified` column missing
**Root Cause:** Docker Desktop not running
**Solution:** Start Docker, apply migrations

