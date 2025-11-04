# Generated manually for marketing module

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('comms', '0002_initial'),
        ('org', '0001_initial'),
        ('patients', '0001_initial'),
        ('services', '0001_initial'),
        ('visits', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SmsProvider',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('api_key', models.CharField(help_text='API key (will be encrypted)', max_length=500)),
                ('api_secret', models.CharField(blank=True, help_text='API secret (will be encrypted)', max_length=500)),
                ('sender_name', models.CharField(help_text='Default sender name', max_length=20)),
                ('rate_limit_per_min', models.IntegerField(default=30, help_text='Rate limit per minute')),
                ('price_per_sms', models.DecimalField(decimal_places=2, default=15.0, help_text='Price per SMS in KZT', max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sms_providers', to='org.organization')),
            ],
            options={
                'verbose_name': 'SMS Provider',
                'verbose_name_plural': 'SMS Providers',
                'db_table': 'sms_providers',
            },
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('channel', models.CharField(choices=[('sms', 'SMS'), ('whatsapp', 'WhatsApp'), ('telegram', 'Telegram')], default='sms', max_length=20)),
                ('sender_name', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('scheduled', 'Scheduled'), ('running', 'Running'), ('paused', 'Paused'), ('finished', 'Finished'), ('failed', 'Failed')], default='draft', max_length=20)),
                ('scheduled_at', models.DateTimeField(blank=True, null=True)),
                ('total_recipients', models.IntegerField(default=0)),
                ('sent_count', models.IntegerField(default=0)),
                ('delivered_count', models.IntegerField(default=0)),
                ('failed_count', models.IntegerField(default=0)),
                ('visit_count', models.IntegerField(default=0, help_text='Визитов после рассылки')),
                ('visit_amount', models.DecimalField(decimal_places=2, default=0, help_text='Сумма визитов', max_digits=12)),
                ('total_cost', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='campaigns_created', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaigns', to='org.organization')),
            ],
            options={
                'verbose_name': 'Campaign',
                'verbose_name_plural': 'Campaigns',
                'db_table': 'campaigns',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CampaignAudience',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('filters', models.JSONField(default=dict, help_text='Audience filters: tags, services, last_visit, birthdate, opt_in')),
                ('campaign', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='audience', to='comms.campaign')),
            ],
            options={
                'db_table': 'campaign_audiences',
            },
        ),
        migrations.CreateModel(
            name='CampaignMessageTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('body', models.TextField(help_text='Message body with placeholders')),
                ('placeholders', models.JSONField(default=list, help_text='Available placeholders')),
                ('max_segments', models.IntegerField(default=1, help_text='Maximum SMS segments')),
                ('campaign', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='message_template', to='comms.campaign')),
            ],
            options={
                'db_table': 'campaign_message_templates',
            },
        ),
        migrations.CreateModel(
            name='CampaignRecipient',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('phone', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('delivered', 'Delivered'), ('failed', 'Failed'), ('opted_out', 'Opted Out')], default='pending', max_length=20)),
                ('provider_msg_id', models.CharField(blank=True, max_length=200)),
                ('error', models.TextField(blank=True)),
                ('cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipients', to='comms.campaign')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaign_recipients', to='patients.patient')),
            ],
            options={
                'db_table': 'campaign_recipients',
                'ordering': ['campaign', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('enabled', models.BooleanField(default=True)),
                ('type', models.CharField(choices=[('MISSED_CALL', 'Пропущенный звонок'), ('PREBOOK_CREATE', 'Создание предварительной записи'), ('PREBOOK_UPDATE', 'Изменение предварительной записи'), ('PREBOOK_DELETE', 'Удаление предварительной записи'), ('PREBOOK_CANCEL', 'Отмена предварительной записи'), ('ONLINE_CONFIRM', 'Подтверждение онлайн-записи'), ('AFTER_VISIT', 'После визита'), ('BIRTHDAY', 'День рождения'), ('BONUS_LEFT', 'Остаток бонусов'), ('BONUS_WRITEOFF', 'Списание бонусов'), ('CUSTOM', 'Произвольное')], max_length=20)),
                ('offset_days', models.IntegerField(default=0, help_text='Дней после события')),
                ('offset_hours', models.IntegerField(default=0, help_text='Часов после события')),
                ('channel', models.CharField(choices=[('sms', 'SMS'), ('call', 'Звонок-робот'), ('whatsapp', 'WhatsApp'), ('telegram', 'Telegram')], default='sms', max_length=20)),
                ('body', models.TextField(help_text='Message body with placeholders')),
                ('sent_count', models.IntegerField(default=0)),
                ('delivered_count', models.IntegerField(default=0)),
                ('visit_count', models.IntegerField(default=0)),
                ('online_bookings_count', models.IntegerField(default=0)),
                ('visit_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reminders_created', to=settings.AUTH_USER_MODEL)),
                ('link_service', models.ForeignKey(blank=True, help_text='Связанная услуга (опционально)', null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.service')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to='org.organization')),
            ],
            options={
                'verbose_name': 'Reminder',
                'verbose_name_plural': 'Reminders',
                'db_table': 'reminders',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ReminderJob',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('scheduled_at', models.DateTimeField(help_text='Scheduled send time')),
                ('status', models.CharField(choices=[('queued', 'Queued'), ('sent', 'Sent'), ('delivered', 'Delivered'), ('failed', 'Failed'), ('skipped', 'Skipped')], default='queued', max_length=20)),
                ('provider_msg_id', models.CharField(blank=True, max_length=200)),
                ('error', models.TextField(blank=True)),
                ('attempts', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='calendar.appointment')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reminder_jobs', to='patients.patient')),
                ('reminder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='comms.reminder')),
                ('visit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='visits.visit')),
            ],
            options={
                'db_table': 'reminder_jobs',
                'ordering': ['scheduled_at'],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('channel', models.CharField(choices=[('sms', 'SMS'), ('whatsapp', 'WhatsApp'), ('telegram', 'Telegram'), ('email', 'Email')], max_length=20)),
                ('body', models.TextField()),
                ('sender', models.CharField(max_length=50)),
                ('context', models.JSONField(default=dict, help_text='Source: campaign/reminder/manual + source_id')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('delivered', 'Delivered'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('provider_msg_id', models.CharField(blank=True, max_length=200)),
                ('error', models.TextField(blank=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='org.organization')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='patients.patient')),
            ],
            options={
                'db_table': 'messages',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SmsBalanceSnapshot',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('period_from', models.DateField()),
                ('period_to', models.DateField()),
                ('sent', models.IntegerField(default=0)),
                ('delivered', models.IntegerField(default=0)),
                ('failed', models.IntegerField(default=0)),
                ('cost', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sms_balance_snapshots', to='org.organization')),
                ('provider', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='comms.smsprovider')),
            ],
            options={
                'db_table': 'sms_balance_snapshots',
                'ordering': ['-period_from'],
            },
        ),
        migrations.CreateModel(
            name='ContactLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('channel', models.CharField(choices=[('sms', 'SMS'), ('whatsapp', 'WhatsApp'), ('telegram', 'Telegram'), ('email', 'Email'), ('call', 'Call')], max_length=20)),
                ('body_hash', models.CharField(help_text='SHA256 hash of message body', max_length=64)),
                ('status', models.CharField(choices=[('sent', 'Sent'), ('delivered', 'Delivered'), ('failed', 'Failed')], max_length=20)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, help_text='Сумма визита', max_digits=12, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='comms.message')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contact_logs', to='org.organization')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contact_logs', to='patients.patient')),
                ('related_visit', models.ForeignKey(blank=True, help_text='Связанный визит (для конверсии)', null=True, on_delete=django.db.models.deletion.SET_NULL, to='visits.visit')),
            ],
            options={
                'db_table': 'contact_logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete'), ('send', 'Send'), ('pause', 'Pause'), ('resume', 'Resume')], max_length=20)),
                ('entity_type', models.CharField(choices=[('campaign', 'Campaign'), ('reminder', 'Reminder'), ('message', 'Message')], max_length=20)),
                ('entity_id', models.UUIDField()),
                ('changes', models.JSONField(default=dict, help_text='Changes made')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='marketing_audit_logs', to='org.organization')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'marketing_audit_logs',
                'ordering': ['-created_at'],
            },
        ),
        # Add indexes
        migrations.AddIndex(
            model_name='campaignrecipient',
            index=models.Index(fields=['campaign', 'status'], name='campaign_re_campaig_idx'),
        ),
        migrations.AddIndex(
            model_name='campaignrecipient',
            index=models.Index(fields=['patient'], name='campaign_re_patient_idx'),
        ),
        migrations.AddIndex(
            model_name='reminder',
            index=models.Index(fields=['organization', 'enabled'], name='reminders_org_enabled_idx'),
        ),
        migrations.AddIndex(
            model_name='reminder',
            index=models.Index(fields=['type'], name='reminders_type_idx'),
        ),
        migrations.AddIndex(
            model_name='reminderjob',
            index=models.Index(fields=['reminder', 'status'], name='reminder_jo_remindr_idx'),
        ),
        migrations.AddIndex(
            model_name='reminderjob',
            index=models.Index(fields=['scheduled_at', 'status'], name='reminder_jo_schedul_idx'),
        ),
        migrations.AddIndex(
            model_name='reminderjob',
            index=models.Index(fields=['patient'], name='reminder_jo_patient_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['organization', 'created_at'], name='messages_org_created_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['patient'], name='messages_patient_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['status'], name='messages_status_idx'),
        ),
        migrations.AddIndex(
            model_name='smsbalancesnapshot',
            index=models.Index(fields=['organization', 'period_from', 'period_to'], name='sms_balance_org_period_idx'),
        ),
        migrations.AddIndex(
            model_name='contactlog',
            index=models.Index(fields=['organization', 'created_at'], name='contact_lo_org_created_idx'),
        ),
        migrations.AddIndex(
            model_name='contactlog',
            index=models.Index(fields=['patient', 'created_at'], name='contact_lo_patient_idx'),
        ),
        migrations.AddIndex(
            model_name='contactlog',
            index=models.Index(fields=['channel'], name='contact_lo_channel_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['organization', 'created_at'], name='audit_logs_org_created_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['entity_type', 'entity_id'], name='audit_logs_entity_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['user'], name='audit_logs_user_idx'),
        ),
    ]

