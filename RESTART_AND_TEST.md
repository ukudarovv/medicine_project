# Restart and Test Guide

## Quick Restart Steps

### 1. Stop Running Services
If services are running, stop them first.

### 2. Restart Backend
```powershell
cd backend
python manage.py runserver
```

### 3. Restart Frontend (in a new terminal)
```powershell
cd frontend
npm run dev
```

## What to Test

### 1. Login
- Login with your user account
- Check browser console for errors

### 2. Organizations Page
- Navigate to Organizations page
- **Before Fix**: You would see `data=[1]` error and empty table
- **After Fix**: Should see proper organization details in table

### 3. All Other Pages
Try visiting these pages (they were showing 500 errors before):
- ✅ Patients
- ✅ Services
- ✅ Staff/Employees
- ✅ Visits
- ✅ Warehouse
- ✅ Billing
- ✅ Calendar/Schedule
- ✅ Marketing
- ✅ Settings

### 4. Check Browser Console
Open browser DevTools (F12) and check:
- **No more Vue warnings** about invalid prop types
- **No more 500 errors** on API calls
- Data loads properly in all tables

## Expected Behavior

### For Regular Users (with Organization)
- Can see only their organization's data
- All pages load without errors
- Proper data in all tables

### For Superusers
- Can see ALL organizations and data
- No filtering applied
- Has access to everything

### For Users Without Organization
- See empty results (no data)
- No 500 errors
- Graceful empty state

## If You Still See Errors

### WebSocket Errors
The console shows WebSocket connection errors - these are normal if the Channels/WebSocket layer isn't configured. They won't affect the main functionality.

### 500 Errors
If you still see 500 errors, check:
1. Is the user logged in?
2. Does the user have an organization assigned?
3. Check backend logs for the actual error

### Frontend Warnings
If you see Vue warnings:
1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R)
3. Check if frontend dev server restarted properly

## Verification Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can login successfully
- [ ] Organizations page shows data correctly
- [ ] No Vue warnings in console
- [ ] No 500 API errors in network tab
- [ ] All pages load data
- [ ] Tables show proper data (not numbers)

## Success Indicators

✅ **Organizations Page**: Shows table with organization objects (ID, Name, SMS Sender, etc.)

✅ **Browser Console**: Clean, no red errors about prop types

✅ **Network Tab**: All API calls return 200 OK (or 403/404 for unauthorized/not found)

✅ **Data Tables**: Show actual data, not numbers or empty

## Still Having Issues?

If problems persist after following this guide:
1. Check `ORGANIZATION_FILTER_FIX_2025-11-05.md` for details on what was fixed
2. Ensure all backend changes were saved
3. Restart both backend and frontend completely
4. Clear browser cache and try in incognito mode
5. Check backend terminal for any Python errors

