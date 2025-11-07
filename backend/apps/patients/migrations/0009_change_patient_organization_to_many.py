# Migration to change Patient.organization from ForeignKey to ManyToManyField

from django.db import migrations, models


def migrate_organization_to_many(apps, schema_editor):
    """
    Migrate existing organization ForeignKey data to ManyToMany relationship
    """
    Patient = apps.get_model('patients', 'Patient')
    db_alias = schema_editor.connection.alias
    
    # For each patient with an organization, add it to the new M2M field
    for patient in Patient.objects.using(db_alias).all():
        if hasattr(patient, 'organization_old') and patient.organization_old:
            patient.organizations.add(patient.organization_old)


def reverse_migration(apps, schema_editor):
    """
    Reverse migration: set organization to first organization from M2M
    """
    Patient = apps.get_model('patients', 'Patient')
    db_alias = schema_editor.connection.alias
    
    for patient in Patient.objects.using(db_alias).all():
        first_org = patient.organizations.first()
        if first_org:
            patient.organization_old = first_org
            patient.save(update_fields=['organization_old'])


class Migration(migrations.Migration):

    dependencies = [
        ('org', '0001_initial'),
        ('patients', '0008_patientverification'),
    ]

    operations = [
        # Step 1: Rename old organization field
        migrations.RenameField(
            model_name='patient',
            old_name='organization',
            new_name='organization_old',
        ),
        
        # Step 2: Create new ManyToManyField
        migrations.AddField(
            model_name='patient',
            name='organizations',
            field=models.ManyToManyField(
                help_text='Организации, в которых зарегистрирован пациент',
                related_name='patients',
                to='org.organization'
            ),
        ),
        
        # Step 3: Migrate data
        migrations.RunPython(migrate_organization_to_many, reverse_migration),
        
        # Step 4: Remove old field
        migrations.RemoveField(
            model_name='patient',
            name='organization_old',
        ),
    ]

