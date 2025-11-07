# Generated manually for PatientVerification model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('org', '0001_initial'),
        ('patients', '0007_add_iin_encryption_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(db_index=True, max_length=20)),
                ('verification_code', models.CharField(max_length=6)),
                ('patient_data', models.JSONField(help_text='Temporary patient data before verification')),
                ('is_verified', models.BooleanField(default=False)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('attempts', models.IntegerField(default=0, help_text='Number of verification attempts')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(help_text='Code expiration time')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patient_verifications', to='org.organization')),
            ],
            options={
                'verbose_name': 'Patient Verification',
                'verbose_name_plural': 'Patient Verifications',
                'db_table': 'patient_verifications',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='patientverification',
            index=models.Index(fields=['phone', 'is_verified'], name='patient_ver_phone_9e18c9_idx'),
        ),
        migrations.AddIndex(
            model_name='patientverification',
            index=models.Index(fields=['expires_at'], name='patient_ver_expires_53b479_idx'),
        ),
    ]

