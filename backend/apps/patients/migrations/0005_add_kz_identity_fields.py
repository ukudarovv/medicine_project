# Generated manually for KZ adaptation

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("patients", "0004_fix_model_fields"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add KZ-specific fields to Patient model
        migrations.AddField(
            model_name="patient",
            name="iin_verified",
            field=models.BooleanField(default=False, help_text="ИИН верифицирован"),
        ),
        migrations.AddField(
            model_name="patient",
            name="iin_verified_at",
            field=models.DateTimeField(
                blank=True, null=True, help_text="Дата верификации ИИН"
            ),
        ),
        migrations.AddField(
            model_name="patient",
            name="kato_address",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Адрес по КАТО (region, district, city, street, building, apartment, kato_code, coordinates)",
            ),
        ),
        migrations.AddField(
            model_name="patient",
            name="osms_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("insured", "Застрахован"),
                    ("not_insured", "Не застрахован"),
                ],
                help_text="Статус ОСМС",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="patient",
            name="osms_category",
            field=models.CharField(
                blank=True,
                choices=[
                    ("employee", "Наемный работник"),
                    ("self_employed", "ИП/Самозанятый"),
                    ("socially_vulnerable", "Социально уязвимый"),
                    ("civil_servant", "Бюджетник"),
                    ("pensioner", "Пенсионер"),
                    ("other", "Другое"),
                ],
                help_text="Категория плательщика ОСМС",
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="patient",
            name="osms_verified_at",
            field=models.DateTimeField(
                blank=True, null=True, help_text="Дата проверки статуса ОСМС"
            ),
        ),
        # Create ConsentHistory model
        migrations.CreateModel(
            name="ConsentHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "consent_type",
                    models.CharField(
                        choices=[
                            ("personal_data", "Обработка персональных данных"),
                            ("medical_intervention", "Медицинское вмешательство"),
                            ("sms_marketing", "SMS-рассылки"),
                            ("whatsapp_marketing", "WhatsApp-рассылки"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("accepted", "Принято"), ("revoked", "Отозвано")],
                        max_length=20,
                    ),
                ),
                (
                    "ip_address",
                    models.GenericIPAddressField(blank=True, null=True),
                ),
                (
                    "user_agent",
                    models.TextField(blank=True, help_text="User agent браузера"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consent_history",
                        to="patients.patient",
                    ),
                ),
                (
                    "accepted_by",
                    models.ForeignKey(
                        blank=True,
                        help_text="Пользователь, который зафиксировал согласие",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accepted_consents",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Consent History",
                "verbose_name_plural": "Consent Histories",
                "db_table": "consent_history",
                "ordering": ["-created_at"],
            },
        ),
        # Add indexes for ConsentHistory
        migrations.AddIndex(
            model_name="consenthistory",
            index=models.Index(
                fields=["patient", "consent_type"], name="consent_his_patient_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="consenthistory",
            index=models.Index(fields=["created_at"], name="consent_his_created_idx"),
        ),
    ]

