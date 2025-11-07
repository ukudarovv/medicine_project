# Generated manually for consent system

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('patients', '0007_add_iin_encryption_fields'),
        ('org', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('scopes', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), default=list, help_text='Requested access scopes (read_summary, read_records, write_records, read_images)', size=None)),
                ('reason', models.TextField(help_text='Reason for requesting access')),
                ('requested_duration_days', models.IntegerField(default=30, help_text='Requested access duration in days')),
                ('status', models.CharField(choices=[('pending', 'Ожидает ответа'), ('approved', 'Одобрено'), ('denied', 'Отклонено'), ('expired', 'Истекло')], db_index=True, default='pending', max_length=20)),
                ('delivery_channel', models.CharField(choices=[('telegram', 'Telegram'), ('sms', 'SMS')], default='telegram', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('expires_at', models.DateTimeField(help_text='Request expiration time (TTL)')),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_requests', to='patients.patient')),
                ('requester_org', models.ForeignKey(help_text='Organization requesting access', on_delete=django.db.models.deletion.CASCADE, related_name='access_requests_made', to='org.organization')),
                ('requester_user', models.ForeignKey(help_text='User who requested access', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='access_requests_made', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Access Request',
                'verbose_name_plural': 'Access Requests',
                'db_table': 'consent_access_requests',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AccessGrant',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('scopes', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), default=list, help_text='Granted access scopes', size=None)),
                ('valid_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('valid_to', models.DateTimeField(help_text='Grant expiration time')),
                ('created_by', models.CharField(default='patient', help_text='Who created this grant (patient, system, admin)', max_length=20)),
                ('is_whitelist', models.BooleanField(default=False, help_text='Long-term trusted access (whitelist)')),
                ('revoked_at', models.DateTimeField(blank=True, help_text='Time when grant was revoked', null=True)),
                ('revocation_reason', models.TextField(blank=True)),
                ('last_accessed_at', models.DateTimeField(blank=True, help_text='Last time this grant was used', null=True)),
                ('access_count', models.IntegerField(default=0, help_text='Number of times this grant was used')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('access_request', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='grant', to='consent.accessrequest')),
                ('grantee_org', models.ForeignKey(help_text='Organization that receives access', on_delete=django.db.models.deletion.CASCADE, related_name='access_grants_received', to='org.organization')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_grants', to='patients.patient')),
                ('revoked_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='revoked_grants', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Access Grant',
                'verbose_name_plural': 'Access Grants',
                'db_table': 'consent_access_grants',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ConsentToken',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('otp_code_hash', models.CharField(help_text='Bcrypt hash of OTP code', max_length=128)),
                ('attempts_count', models.IntegerField(default=0, help_text='Number of verification attempts')),
                ('max_attempts', models.IntegerField(default=3, help_text='Maximum allowed attempts')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(help_text='Token expiration time')),
                ('used_at', models.DateTimeField(blank=True, help_text='Time when token was successfully used', null=True)),
                ('access_request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='consent_token', to='consent.accessrequest')),
            ],
            options={
                'verbose_name': 'Consent Token',
                'verbose_name_plural': 'Consent Tokens',
                'db_table': 'consent_tokens',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(choices=[('read', 'Чтение'), ('write', 'Запись'), ('share', 'Предоставление доступа'), ('revoke', 'Отзыв доступа'), ('request', 'Запрос доступа'), ('deny', 'Отказ в доступе')], db_index=True, max_length=20)),
                ('object_type', models.CharField(blank=True, help_text='Type of object accessed (Visit, PatientFile, etc.)', max_length=50)),
                ('object_id', models.CharField(blank=True, help_text='ID of object accessed', max_length=100)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('details', models.JSONField(blank=True, default=dict, help_text='Additional context and metadata')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('access_grant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to='consent.accessgrant')),
                ('organization', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to='org.organization')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='audit_logs', to='patients.patient')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Audit Log',
                'verbose_name_plural': 'Audit Logs',
                'db_table': 'consent_audit_logs',
                'ordering': ['-created_at'],
                'permissions': [('view_audit_log', 'Can view audit logs')],
            },
        ),
        migrations.AddIndex(
            model_name='accessrequest',
            index=models.Index(fields=['patient', 'status'], name='consent_acc_patient_ff8f8b_idx'),
        ),
        migrations.AddIndex(
            model_name='accessrequest',
            index=models.Index(fields=['requester_org', 'created_at'], name='consent_acc_request_4e4d3f_idx'),
        ),
        migrations.AddIndex(
            model_name='accessrequest',
            index=models.Index(fields=['status', 'expires_at'], name='consent_acc_status_8a5c91_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['patient', 'created_at'], name='consent_aud_patient_d6e8e2_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['user', 'created_at'], name='consent_aud_user_id_8f9c12_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['organization', 'action', 'created_at'], name='consent_aud_organiz_6a4b7e_idx'),
        ),
        migrations.AddIndex(
            model_name='accessgrant',
            index=models.Index(fields=['patient', 'grantee_org'], name='consent_acc_patient_2d3e9f_idx'),
        ),
        migrations.AddIndex(
            model_name='accessgrant',
            index=models.Index(fields=['grantee_org', 'valid_to'], name='consent_acc_grantee_5c7d8a_idx'),
        ),
        migrations.AddIndex(
            model_name='accessgrant',
            index=models.Index(fields=['valid_to', 'revoked_at'], name='consent_acc_valid_t_9e6f2b_idx'),
        ),
    ]

