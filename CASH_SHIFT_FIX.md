# Cash Shift 400 Error - Fix Applied

## Problem
When trying to open a cash shift, users encountered a 400 Bad Request error:
```
api/v1/billing/cashshifts/:1 Failed to load resource: the server responded with a status of 400 (Bad Request)
Failed to open shift: AxiosError
```

## Root Cause
The billing page was not properly loading branches from the API and was using a hardcoded branch ID of `1`, which:
1. May not exist in the database
2. The user may not have access to
3. Was not properly initialized before the shift opening request

## Changes Made

### Frontend (`frontend/src/pages/BillingPage.vue`)

1. **Added Auth Store Integration**
   - Imported `useAuthStore` to access the current branch ID from user session
   - Imported `axios` to make API calls to load branches

2. **Fixed `loadBranches()` Function**
   - Changed from hardcoded mock data to actual API call: `GET /org/branches/`
   - Properly maps branch data to select options
   - Sets default branch from auth store's `currentBranchId`
   - Falls back to first available branch if no branch in auth store
   - Added error handling with user-friendly messages

3. **Updated `loadCurrentShift()` Function**
   - Removed hardcoded branch ID fallback
   - Added validation to skip if no branch is selected
   - Uses actual branch from `shiftForm.value.branch`

4. **Enhanced `handleOpenShift()` Error Handling**
   - Added validation to check if branch is selected before submission
   - Improved error messages to show specific backend validation errors
   - Extracts detailed error messages from API response (e.g., `errorData.branch?.[0]`)

## How It Works Now

1. **On Page Load**:
   - `loadBranches()` fetches real branches from `/org/branches/` API
   - Sets branch to user's current branch from auth store
   - If no current branch, uses first available branch

2. **When Opening Shift**:
   - Validates that a branch is selected
   - Sends branch ID and opening balance to API
   - Shows detailed error if backend validation fails
   - Shows success message and reloads current shift on success

3. **Error Handling**:
   - Clear validation before submission
   - Detailed error messages from backend
   - User-friendly notifications

## Testing

To test the fix:
1. Navigate to the Billing page
2. Click "Открыть смену" (Open Shift)
3. Select a branch from the dropdown (should be auto-populated)
4. Enter opening balance
5. Click to open shift - should succeed

## API Endpoints Used

- `GET /org/branches/` - Load available branches
- `GET /billing/cashshifts/current/?branch={id}` - Get current open shift
- `POST /billing/cashshifts/` - Open new cash shift

## Date
November 5, 2025



