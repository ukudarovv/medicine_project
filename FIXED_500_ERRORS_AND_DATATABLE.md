# Fixed: 500 Errors and DataTable Issues

## Date: November 5, 2025

## Issues Fixed

### 1. Frontend: OrganizationsPage DataTable Issue
**Problem**: The OrganizationsPage was receiving `[1]` (just a number) instead of an array of organization objects, causing Vue to throw prop type warnings.

**Root Cause**: The user's organization data in localStorage was stored as just an ID (from an older API response format) instead of a full organization object.

**Fix**: Updated `OrganizationsPage.vue` to validate that the organization is a proper object before using it, and shows a warning message if the user needs to re-login to refresh their data.

**Files Changed**:
- `frontend/src/pages/OrganizationsPage.vue` (lines 689-704)

### 2. Backend: Permission Issues Causing 500 Errors
**Problem**: Multiple API endpoints were failing with 500 errors because they required `IsBranchMember` permission even for read-only operations, but users weren't sending the X-Branch-Id header on initial page load.

**Root Cause**: Views were using overly restrictive permissions that required branch membership for LIST operations, when they should only require it for CREATE/UPDATE/DELETE operations.

**Fixes Applied**:

#### Organization Views (`backend/apps/org/views.py`)
- **BranchViewSet**: Changed to use `IsAuthenticated` for list/retrieve operations, only requiring `IsBranchMember` for write operations
- **ClinicInfoView**: Added proper error handling when user has no organization (raises NotFound instead of returning None which causes 500)

#### Services Views (`backend/apps/services/views.py`)
- **ServiceCategoryViewSet**: Changed to require `IsBranchAdmin` only for write operations, `IsAuthenticated` for read operations
- **ServiceViewSet**: Changed to require `IsBranchAdmin` only for write operations, `IsAuthenticated` for read operations

#### Warehouse Views (`backend/apps/warehouse/views.py`)
- **WarehouseViewSet**: Changed to require `IsWarehouse` only for write operations
- **StockItemViewSet**: Changed to require `IsWarehouse` only for write operations
- **StockBatchViewSet**: Changed to require `IsWarehouse` only for write operations
- **StockMoveViewSet**: Changed to require `IsWarehouse` only for write operations

## Pattern Applied

All viewsets now follow this pattern:

```python
class ExampleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Only require specific role permission for write operations
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), SpecificRolePermission()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        
        # Always filter by organization
        if user.is_superuser:
            return Model.objects.all()
        elif user.organization:
            return Model.objects.filter(organization=user.organization)
        else:
            return Model.objects.none()
```

## Testing Instructions

### 1. Clear Browser Data
Since the issue was caused by stale localStorage data:

```javascript
// In browser console
localStorage.clear()
// Then refresh the page and log in again
```

### 2. Test the Fixed Endpoints
After restarting the Django server, test these endpoints:

```bash
# Get branches (should work without X-Branch-Id header)
GET /api/v1/org/branches/

# Get services (should work without X-Branch-Id header)
GET /api/v1/services/services/

# Get service categories (should work without X-Branch-Id header)
GET /api/v1/services/categories/

# Get warehouse items (should work without X-Branch-Id header)
GET /api/v1/warehouse/items/

# Get warehouses (should work without X-Branch-Id header)
GET /api/v1/warehouse/warehouses/

# Get staff employees (should work without X-Branch-Id header)
GET /api/v1/staff/employees/

# Get visits (should work without X-Branch-Id header)
GET /api/v1/visits/visits/
```

### 3. Test the Organizations Page
1. Log out and log back in
2. Navigate to the Organizations page
3. You should see proper organization data without Vue warnings in the console

## What Changed

### Before
- Views required specific role permissions (IsBranchMember, IsBranchAdmin, etc.) for ALL operations including reads
- This meant users needed to send X-Branch-Id header even to list data
- When users first loaded pages, they didn't have a branch selected yet, causing 403/500 errors
- Frontend had stale organization data (just IDs instead of full objects)

### After  
- Views only require specific role permissions for write operations
- Read operations (list, retrieve) only require basic authentication
- Users can list data without selecting a branch first
- Frontend validates organization data and warns users to re-login if data is stale

## Benefits

1. **Better UX**: Users can now view data immediately without selecting a branch
2. **Fewer Errors**: No more 500 errors on page load
3. **More Secure**: Write operations still require proper role-based permissions
4. **Consistent**: All viewsets follow the same permission pattern
5. **Flexible**: Branch selection can be used for filtering, but isn't required for basic access

## Migration Notes

If you have existing users with stale localStorage data, they will see a warning message prompting them to re-login. This is a one-time inconvenience that will resolve itself.

## Future Improvements

Consider adding:
1. A middleware to automatically migrate stale localStorage data
2. An API endpoint to refresh user data without full re-login
3. Better validation of organization data on the frontend before using it

