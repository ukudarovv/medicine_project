# Generated manually for Sprint 2

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("visits", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add Sprint 2 fields to Visit
        migrations.AddField(
            model_name="visit",
            name="diary_structured",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Структурированный дневник: complaints, anamnesis, examination, conclusion, recommendations",
            ),
        ),
        migrations.AddField(
            model_name="visit",
            name="templates_used",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="ID шаблонов, использованных при записи",
            ),
        ),
        # Create VisitFile model
        migrations.CreateModel(
            name="VisitFile",
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
                    "file",
                    models.FileField(upload_to="visits/%Y/%m/"),
                ),
                (
                    "file_type",
                    models.CharField(
                        choices=[
                            ("xray", "Рентген"),
                            ("photo", "Фото"),
                            ("document", "Документ"),
                            ("lab_result", "Результат анализа"),
                            ("other", "Другое"),
                        ],
                        default="other",
                        max_length=20,
                    ),
                ),
                ("title", models.CharField(blank=True, max_length=200)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "visit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="files",
                        to="visits.visit",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Visit File",
                "verbose_name_plural": "Visit Files",
                "db_table": "visit_files",
                "ordering": ["-created_at"],
            },
        ),
    ]

