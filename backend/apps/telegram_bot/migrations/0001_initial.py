# Generated manually for telegram_bot

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('patients', '0008_patientverification'),
        ('calendar', '0004_add_break_model'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('org', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientTelegramLink',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('telegram_user_id', models.BigIntegerField(db_index=True, help_text='Telegram user ID', unique=True)),
                ('telegram_username', models.CharField(blank=True, help_text='Telegram username (@username)', max_length=100)),
                ('language', models.CharField(choices=[('ru', 'Русский'), ('kk', 'Қазақ')], default='ru', help_text='Preferred language', max_length=2)),
                ('consents_json', models.JSONField(default=dict, help_text='Consents: personal_data, medical_intervention, marketing')),
                ('is_active', models.BooleanField(default=True)),
                ('last_interaction_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='telegram_link', to='patients.patient')),
            ],
            options={
                'verbose_name': 'Patient Telegram Link',
                'verbose_name_plural': 'Patient Telegram Links',
                'db_table': 'patient_telegram_links',
                'indexes': [
                    models.Index(fields=['telegram_user_id'], name='patient_tel_telegra_f8e7c3_idx'),
                    models.Index(fields=['patient'], name='patient_tel_patient_3b8a6c_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='BotBroadcast',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(help_text='Название рассылки', max_length=200)),
                ('segment_filters_json', models.JSONField(default=dict, help_text='Filters: age_min, age_max, sex, services, tags, osms_status, last_visit_from, last_visit_to')),
                ('text_ru', models.TextField(help_text='Текст на русском')),
                ('text_kk', models.TextField(blank=True, help_text='Текст на казахском')),
                ('status', models.CharField(choices=[('draft', 'Черновик'), ('scheduled', 'Запланирована'), ('running', 'Выполняется'), ('completed', 'Завершена'), ('failed', 'Ошибка')], default='draft', max_length=20)),
                ('scheduled_at', models.DateTimeField(blank=True, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('total_recipients', models.IntegerField(default=0)),
                ('sent_count', models.IntegerField(default=0)),
                ('delivered_count', models.IntegerField(default=0)),
                ('failed_count', models.IntegerField(default=0)),
                ('clicked_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bot_broadcasts', to='org.organization')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bot_broadcasts_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Bot Broadcast',
                'verbose_name_plural': 'Bot Broadcasts',
                'db_table': 'bot_broadcasts',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['organization', 'status'], name='bot_broadca_organiz_8c5e8e_idx'),
                    models.Index(fields=['scheduled_at'], name='bot_broadca_schedul_7f6e5b_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='BotDocument',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('document_type', models.CharField(choices=[('direction', 'Направление'), ('recipe', 'Рецепт'), ('tax', 'Справка для налогового вычета'), ('result', 'Результат исследования'), ('certificate', 'Справка')], max_length=20)),
                ('file_path', models.CharField(help_text='Path to PDF file', max_length=500)),
                ('title', models.CharField(max_length=200)),
                ('language', models.CharField(choices=[('ru', 'Русский'), ('kk', 'Қазақ')], default='ru', max_length=2)),
                ('expires_at', models.DateTimeField(help_text='Link expiration time')),
                ('is_expired', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bot_documents', to='patients.patient')),
                ('related_visit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='visits.visit')),
            ],
            options={
                'verbose_name': 'Bot Document',
                'verbose_name_plural': 'Bot Documents',
                'db_table': 'bot_documents',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['patient', 'document_type'], name='bot_documen_patient_5c8e7d_idx'),
                    models.Index(fields=['expires_at'], name='bot_documen_expires_8f6e5b_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='BotAudit',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(choices=[('register', 'Регистрация'), ('book', 'Запись на приём'), ('cancel', 'Отмена записи'), ('reschedule', 'Перенос записи'), ('view_doc', 'Просмотр документа'), ('payment', 'Оплата'), ('feedback', 'Обратная связь'), ('other', 'Другое')], max_length=20)),
                ('payload_json', models.JSONField(default=dict, help_text='Action details and metadata')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.CharField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patient_telegram_link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='audit_logs', to='telegram_bot.patienttelegramlink')),
            ],
            options={
                'verbose_name': 'Bot Audit Log',
                'verbose_name_plural': 'Bot Audit Logs',
                'db_table': 'bot_audit_logs',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['patient_telegram_link', 'created_at'], name='bot_audit_l_patient_5c8e7d_idx'),
                    models.Index(fields=['action'], name='bot_audit_l_action_8f6e5b_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='BotFeedback',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('score', models.IntegerField(help_text='NPS score 0-10')),
                ('comment', models.TextField(blank=True, help_text='Optional comment')),
                ('is_low_score', models.BooleanField(default=False, help_text='True if score <= 6')),
                ('is_reviewed', models.BooleanField(default=False, help_text='Admin reviewed the feedback')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bot_feedbacks', to='calendar.appointment')),
                ('patient_telegram_link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='telegram_bot.patienttelegramlink')),
            ],
            options={
                'verbose_name': 'Bot Feedback',
                'verbose_name_plural': 'Bot Feedbacks',
                'db_table': 'bot_feedbacks',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['appointment'], name='bot_feedbac_appoint_5c8e7d_idx'),
                    models.Index(fields=['score'], name='bot_feedbac_score_8f6e5b_idx'),
                    models.Index(fields=['is_low_score', 'is_reviewed'], name='bot_feedbac_is_low__9c8e7d_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='SupportTicket',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('subject', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[('open', 'Открыт'), ('in_progress', 'В работе'), ('resolved', 'Решён'), ('closed', 'Закрыт')], default='open', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('patient_telegram_link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='support_tickets', to='telegram_bot.patienttelegramlink')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tickets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Support Ticket',
                'verbose_name_plural': 'Support Tickets',
                'db_table': 'support_tickets',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['patient_telegram_link', 'status'], name='support_tic_patient_5c8e7d_idx'),
                    models.Index(fields=['status', 'created_at'], name='support_tic_status_8f6e5b_idx'),
                ],
            },
        ),
    ]


