# Generated manually to fix model field inconsistencies

from django.db import migrations, models


def split_contact_person_name(apps, schema_editor):
    """Split 'name' field into 'first_name' and 'last_name'"""
    PatientContactPerson = apps.get_model('patients', 'PatientContactPerson')
    for contact in PatientContactPerson.objects.all():
        parts = contact.name.split(' ', 1)
        contact.first_name = parts[0] if len(parts) > 0 else ''
        contact.last_name = parts[1] if len(parts) > 1 else ''
        contact.save(update_fields=['first_name', 'last_name'])


def merge_contact_person_name(apps, schema_editor):
    """Merge 'first_name' and 'last_name' back into 'name'"""
    PatientContactPerson = apps.get_model('patients', 'PatientContactPerson')
    for contact in PatientContactPerson.objects.all():
        contact.name = f"{contact.first_name} {contact.last_name}".strip()
        contact.save(update_fields=['name'])


def convert_diagnosis_is_primary_to_type(apps, schema_editor):
    """Convert is_primary (boolean) to type (CharField)"""
    PatientDiagnosis = apps.get_model('patients', 'PatientDiagnosis')
    for diagnosis in PatientDiagnosis.objects.all():
        diagnosis.type = '1' if diagnosis.is_primary else '2'
        diagnosis.save(update_fields=['type'])


def convert_diagnosis_type_to_is_primary(apps, schema_editor):
    """Convert type (CharField) back to is_primary (boolean)"""
    PatientDiagnosis = apps.get_model('patients', 'PatientDiagnosis')
    for diagnosis in PatientDiagnosis.objects.all():
        diagnosis.is_primary = (diagnosis.type == '1')
        diagnosis.save(update_fields=['is_primary'])


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0003_patient_marketing_fields'),
    ]

    operations = [
        # Step 1: Rename phone_type to type in PatientPhone
        migrations.RenameField(
            model_name='patientphone',
            old_name='phone_type',
            new_name='type',
        ),
        # Step 2: Add note field to PatientPhone
        migrations.AddField(
            model_name='patientphone',
            name='note',
            field=models.CharField(blank=True, max_length=200),
        ),
        # Step 3: Add first_name and last_name to PatientContactPerson
        migrations.AddField(
            model_name='patientcontactperson',
            name='first_name',
            field=models.CharField(max_length=100, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patientcontactperson',
            name='last_name',
            field=models.CharField(max_length=100, default=''),
            preserve_default=False,
        ),
        # Step 4: Split name into first_name and last_name
        migrations.RunPython(split_contact_person_name, merge_contact_person_name),
        # Step 5: Remove old name field
        migrations.RemoveField(
            model_name='patientcontactperson',
            name='name',
        ),
        # Step 6: Add email and note to PatientContactPerson
        migrations.AddField(
            model_name='patientcontactperson',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='patientcontactperson',
            name='note',
            field=models.TextField(blank=True),
        ),
        # Step 7: Add url field to PatientSocialNetwork
        migrations.AddField(
            model_name='patientsocialnetwork',
            name='url',
            field=models.URLField(blank=True),
        ),
        # Step 8: Add notes field to PatientDisease
        migrations.AddField(
            model_name='patientdisease',
            name='notes',
            field=models.TextField(blank=True),
        ),
        # Step 9: Add type field to PatientDiagnosis
        migrations.AddField(
            model_name='patientdiagnosis',
            name='type',
            field=models.CharField(
                choices=[('1', 'Первичный'), ('2', 'Повторный')],
                default='1',
                max_length=1
            ),
        ),
        # Step 10: Convert is_primary to type
        migrations.RunPython(convert_diagnosis_is_primary_to_type, convert_diagnosis_type_to_is_primary),
        # Step 11: Remove old is_primary field
        migrations.RemoveField(
            model_name='patientdiagnosis',
            name='is_primary',
        ),
    ]

