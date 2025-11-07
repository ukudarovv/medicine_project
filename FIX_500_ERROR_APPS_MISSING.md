# Fix for 500 Internal Server Errors - November 5, 2025

## Problem Identified

All API endpoints were returning `500 Internal Server Error` because the backend Django application was configured to load three apps that **do not exist in the Docker container**:

- `apps.consent`
- `apps.ehr`
- `apps.telegram_bot`

These apps were referenced in:
1. `backend/config/settings/base.py` - in `INSTALLED_APPS`
2. `backend/config/settings/base.py` - in `MIDDLEWARE` (ConsentCheckMiddleware)
3. `backend/config/urls.py` - in URL patterns

## Root Cause

The Docker images were built **before** these apps were created in the source code. When Django tried to initialize with these apps in the configuration, it failed to start properly, causing all requests to return 500 errors.

## Solution Applied

Temporarily commented out the missing apps and middleware in the configuration files:

### Changes Made:

1. **backend/config/settings/base.py** - INSTALLED_APPS:
   ```python
   # 'apps.telegram_bot',  # Temporarily disabled - app not in container
   # 'apps.consent',  # Temporarily disabled - app not in container
   # 'apps.ehr',  # Temporarily disabled - app not in container
   ```

2. **backend/config/settings/base.py** - MIDDLEWARE:
   ```python
   # 'apps.consent.middleware.ConsentCheckMiddleware',  # Temporarily disabled - app not in container
   ```

3. **backend/config/urls.py** - URL patterns:
   ```python
   # path('consent/', include('apps.consent.urls')),  # Temporarily disabled - app not in container
   # path('ehr/', include('apps.ehr.urls')),  # Temporarily disabled - app not in container
   # path('api/bot/', include('apps.telegram_bot.urls')),  # Temporarily disabled - app not in container
   ```

4. Restarted the backend container:
   ```bash
   docker restart kudarovumar-backend-1
   ```

## Status

✅ Backend server is now running successfully
✅ Django system check passes (only 1 minor staticfiles warning)
✅ API endpoints should now be accessible

## Long-term Solution

To properly enable the `consent`, `ehr`, and `telegram_bot` apps, you need to:

### Option 1: Rebuild Docker Images (Recommended)

```bash
# Stop all containers
docker-compose down

# Rebuild images
docker-compose build

# Start containers
docker-compose up -d

# Apply migrations for new apps
docker exec kudarovumar-backend-1 python manage.py migrate

# Then uncomment all the apps in settings and urls
```

### Option 2: Copy Apps to Running Container (Temporary)

```bash
# Copy apps to container
docker cp backend/apps/consent kudarovumar-backend-1:/app/apps/
docker cp backend/apps/ehr kudarovumar-backend-1:/app/apps/
docker cp backend/apps/telegram_bot kudarovumar-backend-1:/app/apps/

# Restart container
docker restart kudarovumar-backend-1

# Apply migrations
docker exec kudarovumar-backend-1 python manage.py migrate

# Then uncomment all the apps in settings and urls
```

## After Enabling Apps

Once the apps are in the container, uncomment:
1. The three apps in `INSTALLED_APPS`
2. The `ConsentCheckMiddleware` in `MIDDLEWARE`
3. The three URL patterns in `config/urls.py`
4. Restart the backend container

## Testing

After restart, test that endpoints are working:
- http://localhost:8000/api/v1/patients/patients/
- http://localhost:8000/api/v1/staff/employees/
- http://localhost:8000/api/v1/org/clinic-info/
- http://localhost:8000/api/v1/services/services/

All should return data (possibly empty arrays) instead of 500 errors.

## Notes

- The WebSocket errors (`/ws/calendar/3`) are separate - those require the `channels` container to be running properly
- The frontend at `http://localhost:5173` should now load properly without 500 errors on all pages

