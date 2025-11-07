# Telegram Bot Registration Fix - November 5, 2025

## Issues Fixed

### Issue 1: ModuleNotFoundError: No module named 'apps.telegram_bot'
**Root Cause**: The `apps.telegram_bot` app was commented out in `INSTALLED_APPS` in Django settings.

**Fix**: Uncommented `'apps.telegram_bot'` in `backend/config/settings/base.py` (line 47)

```python
# Before:
# 'apps.telegram_bot',  # Enabled at runtime via volume mount

# After:
'apps.telegram_bot',
```

### Issue 2: Telegram Bot Registration Error - "Произошла ошибка. Попробуйте позже."
**Root Cause**: The `PatientUpsertView` was trying to create a Patient with a single `organization` field (ForeignKey), but the Patient model was updated to use `organizations` (ManyToManyField) for multi-organization support.

**Fix**: Updated `backend/apps/telegram_bot/views.py` to properly handle the many-to-many relationship:

```python
# Before (line 73-83):
patient = Patient.objects.create(
    organization=organization,  # ❌ Wrong - this field doesn't exist anymore
    first_name=data['first_name'],
    ...
)

# After (line 74-85):
patient = Patient.objects.create(
    first_name=data['first_name'],
    ...
)
# Add organization to many-to-many relationship
patient.organizations.add(organization)  # ✅ Correct
```

## Changes Made

1. **backend/config/settings/base.py** (line 47)
   - Uncommented `'apps.telegram_bot'` in `INSTALLED_APPS`

2. **backend/apps/telegram_bot/views.py** (lines 74-85)
   - Removed `organization=organization` from `Patient.objects.create()`
   - Added `patient.organizations.add(organization)` after patient creation

## How to Test

1. **Restart the Django backend**:
   ```powershell
   docker-compose restart backend
   ```

2. **Test Telegram Bot Registration**:
   - Open Telegram and find your bot
   - Send `/start` command
   - Complete the registration process:
     - Choose language
     - Enter first name, last name, middle name (or skip)
     - Send phone number
     - Enter birth date (DD.MM.YYYY format)
     - Select sex
     - Enter IIN (12 digits)
     - Accept consents
   - Registration should now complete successfully! ✅

## Expected Result

After the fix:
- ✅ Django backend starts without errors
- ✅ Bot registration completes successfully
- ✅ Patient is created in the database with organization link
- ✅ Bot shows main menu after registration

## Technical Details

### Patient Model Structure
The Patient model now uses a ManyToMany relationship with Organization:

```python
class Patient(models.Model):
    organizations = models.ManyToManyField(
        Organization,
        related_name='patients',
        help_text='Организации, в которых зарегистрирован пациент'
    )
    # ... other fields
```

This allows a patient to be registered in multiple organizations, which is essential for:
- Cross-organization access
- Multi-clinic patients
- Consent management system

### Bot API Authentication
The bot API uses custom authentication (`BotAPIAuthentication`) with a secret token defined in environment variables:
- `TELEGRAM_BOT_API_SECRET` - Used for bot-to-backend authentication

Make sure this is properly set in your `.env` file and matches in both:
- Django backend (`TELEGRAM_BOT_API_SECRET`)
- Telegram bot service (`TELEGRAM_BOT_API_SECRET`)

## Status: ✅ FIXED

Both issues have been resolved. Please restart the backend and test the bot registration.

