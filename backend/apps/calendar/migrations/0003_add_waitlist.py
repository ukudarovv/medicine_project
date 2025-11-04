# Generated manually for Sprint 2

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("calendar", "0002_initial"),
        ("patients", "0005_add_kz_identity_fields"),
        ("staff", "0004_migrate_legacy_data"),
        ("services", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Waitlist",
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
                    "preferred_date",
                    models.DateField(blank=True, null=True, help_text="Конкретная дата"),
                ),
                (
                    "preferred_period_start",
                    models.DateField(blank=True, null=True, help_text="Начало периода"),
                ),
                (
                    "preferred_period_end",
                    models.DateField(blank=True, null=True, help_text="Конец периода"),
                ),
                (
                    "time_window",
                    models.CharField(
                        choices=[
                            ("morning", "Утро (9:00-12:00)"),
                            ("afternoon", "День (12:00-17:00)"),
                            ("evening", "Вечер (17:00-20:00)"),
                            ("any", "Любое время"),
                        ],
                        default="any",
                        max_length=20,
                    ),
                ),
                (
                    "priority",
                    models.IntegerField(default=0, help_text="Приоритет (0=обычный, выше=важнее)"),
                ),
                ("comment", models.TextField(blank=True, help_text="Комментарий")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("waiting", "Ожидает"),
                            ("contacted", "Связались"),
                            ("scheduled", "Записан"),
                            ("cancelled", "Отменен"),
                        ],
                        default="waiting",
                        max_length=20,
                    ),
                ),
                ("contacted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "contact_result",
                    models.TextField(blank=True, help_text="Результат связи"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="waitlist_entries",
                        to="patients.patient",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        blank=True,
                        help_text="Желаемая услуга",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="services.service",
                    ),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        blank=True,
                        help_text="Желаемый врач",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="staff.employee",
                    ),
                ),
                (
                    "contacted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="waitlist_contacts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Waitlist Entry",
                "verbose_name_plural": "Waitlist Entries",
                "db_table": "waitlist",
                "ordering": ["-priority", "created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="waitlist",
            index=models.Index(fields=["patient", "status"], name="waitlist_patient_status_idx"),
        ),
        migrations.AddIndex(
            model_name="waitlist",
            index=models.Index(fields=["status", "preferred_date"], name="waitlist_status_date_idx"),
        ),
    ]

