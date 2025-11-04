# Data migration to copy legacy fields and create Position records
from django.db import migrations


def migrate_data_forward(apps, schema_editor):
    """
    Copy legacy fields to new fields and create Position records from position_legacy strings
    """
    Employee = apps.get_model('staff', 'Employee')
    Position = apps.get_model('staff', 'Position')
    
    # Dictionary to cache created positions
    position_cache = {}
    
    for employee in Employee.objects.all():
        # Copy hire_date to hired_at
        if employee.hire_date and not employee.hired_at:
            employee.hired_at = employee.hire_date
        
        # Copy fire_date to fired_at
        if employee.fire_date and not employee.fired_at:
            employee.fired_at = employee.fire_date
        
        # Copy color to calendar_color
        if employee.color and employee.calendar_color == '#2196F3':
            employee.calendar_color = employee.color
        
        # Set employment status based on fire dates
        if employee.fired_at or employee.fire_date:
            employee.employment_status = 'fired'
        else:
            employee.employment_status = 'active'
        
        # Set is_user_enabled based on user field
        if employee.user_id:
            employee.is_user_enabled = True
        
        # Create Position object from position_legacy if not empty
        if employee.position_legacy and employee.position_legacy.strip():
            position_name = employee.position_legacy.strip()
            
            # Use cache to avoid duplicate Position creation
            cache_key = f"{employee.organization_id}_{position_name}"
            
            if cache_key not in position_cache:
                # Try to find existing position or create new one
                position, created = Position.objects.get_or_create(
                    organization_id=employee.organization_id,
                    name=position_name,
                    defaults={
                        'comment': '',
                        'hidden_in_schedule_filter': False
                    }
                )
                position_cache[cache_key] = position
            
            # Link employee to Position
            employee.position = position_cache[cache_key]
        
        employee.save()


def migrate_data_backward(apps, schema_editor):
    """
    Reverse migration - copy Position name back to position_legacy
    """
    Employee = apps.get_model('staff', 'Employee')
    
    for employee in Employee.objects.all():
        if employee.position:
            employee.position_legacy = employee.position.name
            employee.save()


class Migration(migrations.Migration):
    dependencies = [
        ('staff', '0003_salaryschematemplate_employee_access_template_id_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_data_forward, migrate_data_backward),
    ]

