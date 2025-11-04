# Generated manually for Sprint 2

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("comms", "0003_marketing_models"),
        ("patients", "0005_add_kz_identity_fields"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PatientContact",
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
                    "contact_type",
                    models.CharField(
                        choices=[
                            ("call", "Звонок"),
                            ("sms", "SMS"),
                            ("whatsapp", "WhatsApp"),
                            ("visit", "Визит в клинику"),
                            ("email", "Email"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "direction",
                    models.CharField(
                        choices=[
                            ("inbound", "Входящий"),
                            ("outbound", "Исходящий"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("reached", "Дозвонились"),
                            ("no_answer", "Не ответил"),
                            ("callback_requested", "Перезвонить"),
                            ("message_left", "Оставлено сообщение"),
                            ("completed", "Выполнено"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "note",
                    models.TextField(blank=True, help_text="Заметка о контакте"),
                ),
                (
                    "next_contact_date",
                    models.DateTimeField(
                        blank=True, null=True, help_text="Дата следующего контакта"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contact_interactions",
                        to="patients.patient",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="patient_contacts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Patient Contact",
                "verbose_name_plural": "Patient Contacts",
                "db_table": "patient_contacts",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="patientcontact",
            index=models.Index(
                fields=["patient", "created_at"], name="patient_contacts_patient_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="patientcontact",
            index=models.Index(
                fields=["contact_type", "status"], name="patient_contacts_type_status_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="patientcontact",
            index=models.Index(
                fields=["next_contact_date"], name="patient_contacts_next_idx"
            ),
        ),
    ]

