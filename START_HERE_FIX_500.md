# 🚨 FIX 500 ERROR - START HERE

## Problem

Your application is showing **500 Internal Server Error** on all pages because:

1. ❌ **Docker Desktop is NOT running**
2. ❌ **Database migrations are not applied**
3. ❌ **Backend server is not running**

## Root Cause

The database is missing the column `patients.iin_verified` and other fields. These fields are defined in Django migrations but haven't been applied to the database because Docker is not running.

## Quick Fix (3 Steps)

### ✅ Step 1: Start Docker Desktop

**You must do this manually:**

1. Open **Docker Desktop** application
2. Wait until Docker is fully running (whale icon in system tray stops animating)
3. Verify it's running by opening a new PowerShell and typing:
   ```powershell
   docker ps
   ```
   You should see a table (even if empty), not an error message

### ✅ Step 2: Run the Start Script

Once Docker is running, right-click **start_project.ps1** and select **Run with PowerShell**

OR in PowerShell:

```powershell
cd "C:\Users\Kudarov Umar\Desktop\My Projects\Medicine"
powershell -ExecutionPolicy Bypass -File start_project.ps1
```

This will:
- Start all Docker containers (database, Redis, backend, frontend, etc.)
- Apply all database migrations
- Show you the URLs to access the app

### ✅ Step 3: Access Your Application

Open your browser and go to:
- **Frontend:** http://localhost:5173
- **Admin Panel:** http://localhost:8000/admin/

The 500 errors should be gone! ✨

---

## Manual Alternative (If Script Fails)

If the script doesn't work, run these commands manually in PowerShell:

```powershell
# 1. Navigate to project
cd "C:\Users\Kudarov Umar\Desktop\My Projects\Medicine"

# 2. Start all containers
docker-compose up -d

# 3. Wait 15 seconds for services to start
Start-Sleep -Seconds 15

# 4. Apply migrations
docker-compose exec backend python manage.py migrate

# 5. Check status
docker-compose ps
```

---

## Still Having Issues?

### Check Container Logs

```powershell
# Backend logs
docker-compose logs backend -f

# Database logs
docker-compose logs db

# All logs
docker-compose logs
```

### Restart Everything

```powershell
docker-compose down
docker-compose up -d
Start-Sleep -Seconds 15
docker-compose exec backend python manage.py migrate
```

### Check Port Conflicts

If containers won't start:

```powershell
# Check what's using ports
netstat -ano | findstr :5432   # PostgreSQL
netstat -ano | findstr :6379   # Redis (already freed)
netstat -ano | findstr :8000   # Backend
netstat -ano | findstr :5173   # Frontend

# Kill process if needed
taskkill /PID <PID_NUMBER> /F
```

---

## What We Fixed

✅ Stopped local Redis service (was blocking port 6379)  
✅ Created automated start script  
✅ Documented the issue and solution  

**You need to do:**  
🔲 Start Docker Desktop  
🔲 Run start_project.ps1  
🔲 Access http://localhost:5173  

---

**Created:** November 5, 2025  
**Next Step:** START DOCKER DESKTOP, then run start_project.ps1

