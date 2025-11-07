# Generated manually to fix AppointmentResource missing foreign keys

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("calendar", "0004_add_break_model"),
        ("org", "0001_initial"),
        ("patients", "0009_change_patient_organization_to_many"),
        ("services", "0002_initial"),
        ("staff", "0004_migrate_legacy_data"),  # Fixed - was referencing non-existent 0005
    ]

    operations = [
        # Add missing foreign keys to AppointmentResource ONLY
        migrations.AddField(
            model_name="appointmentresource",
            name="appointment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="allocated_resources",
                to="calendar.appointment",
                null=True,  # Temporarily nullable for migration
            ),
        ),
        migrations.AddField(
            model_name="appointmentresource",
            name="resource",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="appointment_allocations",
                to="org.resource",
                null=True,  # Temporarily nullable for migration
            ),
        ),
        
        # Add unique constraint
        migrations.AlterUniqueTogether(
            name="appointmentresource",
            unique_together={("appointment", "resource")},
        ),
    ]

