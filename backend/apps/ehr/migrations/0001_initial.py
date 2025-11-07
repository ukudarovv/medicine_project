# Generated manually for EHR system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('patients', '0007_add_iin_encryption_fields'),
        ('org', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EHRRecord',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('record_type', models.CharField(choices=[('visit_note', 'Запись визита'), ('diagnosis', 'Диагноз'), ('prescription', 'Рецепт'), ('lab_result', 'Результат анализа'), ('image', 'Изображение'), ('document', 'Документ'), ('procedure', 'Процедура'), ('allergy', 'Аллергия'), ('vaccination', 'Прививка'), ('other', 'Другое')], db_index=True, max_length=50)),
                ('title', models.CharField(help_text='Record title/summary', max_length=500)),
                ('payload', models.JSONField(default=dict, help_text='Record data (structure depends on record_type)')),
                ('object_id', models.CharField(blank=True, help_text='ID of related object', max_length=100)),
                ('version', models.IntegerField(default=1, help_text='Version number for this record')),
                ('is_external', models.BooleanField(default=False, help_text='Created by external organization (via consent)')),
                ('is_deleted', models.BooleanField(default=False, help_text='Soft delete flag')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('author', models.ForeignKey(help_text='User who created this record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ehr_records_authored', to=settings.AUTH_USER_MODEL)),
                ('content_type', models.ForeignKey(blank=True, help_text='Type of related object (Visit, PatientFile, etc.)', null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.contenttype')),
                ('organization', models.ForeignKey(help_text='Organization that created this record', on_delete=django.db.models.deletion.CASCADE, related_name='ehr_records', to='org.organization')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ehr_records', to='patients.patient')),
                ('previous_version', models.ForeignKey(blank=True, help_text='Previous version of this record (if edited)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='next_versions', to='ehr.ehrrecord')),
            ],
            options={
                'verbose_name': 'EHR Record',
                'verbose_name_plural': 'EHR Records',
                'db_table': 'ehr_records',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='ehrrecord',
            index=models.Index(fields=['patient', 'record_type', 'created_at'], name='ehr_records_patient_8a4f9e_idx'),
        ),
        migrations.AddIndex(
            model_name='ehrrecord',
            index=models.Index(fields=['organization', 'created_at'], name='ehr_records_organiz_5e7c2d_idx'),
        ),
        migrations.AddIndex(
            model_name='ehrrecord',
            index=models.Index(fields=['record_type', 'created_at'], name='ehr_records_record__9f6b3a_idx'),
        ),
        migrations.AddIndex(
            model_name='ehrrecord',
            index=models.Index(fields=['is_deleted', 'created_at'], name='ehr_records_is_dele_4d8e1c_idx'),
        ),
    ]

