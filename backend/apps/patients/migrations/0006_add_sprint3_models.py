# Generated manually for Sprint 3

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("patients", "0005_add_kz_identity_fields"),
        ("services", "0002_initial"),
        ("org", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Medical Examination model
        migrations.CreateModel(
            name="MedicalExamination",
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
                    "exam_type",
                    models.CharField(
                        choices=[
                            ("preliminary", "Предварительный"),
                            ("periodic", "Периодический"),
                            ("extraordinary", "Внеочередной"),
                        ],
                        max_length=20,
                    ),
                ),
                ("exam_date", models.DateField(help_text="Дата проведения осмотра")),
                ("work_profile", models.TextField(blank=True, help_text="Профиль работы, условия труда")),
                ("conclusion", models.TextField(blank=True, help_text="Заключение комиссии")),
                ("fit_for_work", models.BooleanField(default=True, help_text="Годен к работе")),
                ("restrictions", models.TextField(blank=True, help_text="Ограничения и рекомендации")),
                ("next_exam_date", models.DateField(blank=True, null=True, help_text="Дата следующего осмотра")),
                ("commission_members", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="medical_examinations",
                        to="patients.patient",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_exams",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Medical Examination",
                "verbose_name_plural": "Medical Examinations",
                "db_table": "medical_examinations",
                "ordering": ["-exam_date"],
            },
        ),
        # MedExamPastDisease
        migrations.CreateModel(
            name="MedExamPastDisease",
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
                ("disease_name", models.CharField(max_length=300)),
                ("year", models.IntegerField()),
                ("note", models.TextField(blank=True)),
                (
                    "examination",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="past_diseases",
                        to="patients.medicalexamination",
                    ),
                ),
                (
                    "icd_code",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="services.icdcode",
                    ),
                ),
            ],
            options={
                "verbose_name": "Medical Exam Past Disease",
                "verbose_name_plural": "Medical Exam Past Diseases",
                "db_table": "medexam_past_diseases",
                "ordering": ["-year"],
            },
        ),
        # MedExamVaccination
        migrations.CreateModel(
            name="MedExamVaccination",
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
                ("vaccine_type", models.CharField(max_length=200)),
                ("date", models.DateField()),
                ("revaccination_date", models.DateField(blank=True, null=True)),
                ("serial_number", models.CharField(blank=True, max_length=100)),
                ("note", models.TextField(blank=True)),
                (
                    "examination",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vaccinations",
                        to="patients.medicalexamination",
                    ),
                ),
            ],
            options={
                "verbose_name": "Medical Exam Vaccination",
                "verbose_name_plural": "Medical Exam Vaccinations",
                "db_table": "medexam_vaccinations",
                "ordering": ["-date"],
            },
        ),
        # MedExamLabTest
        migrations.CreateModel(
            name="MedExamLabTest",
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
                    "test_type",
                    models.CharField(
                        choices=[
                            ("blood_general", "ОАК (Общий анализ крови)"),
                            ("blood_biochem", "Биохимия крови"),
                            ("urine", "ОАМ (Общий анализ мочи)"),
                            ("ecg", "ЭКГ"),
                            ("xray", "Рентгенография"),
                            ("fluorography", "Флюорография"),
                            ("spirometry", "Спирометрия"),
                            ("audiometry", "Аудиометрия"),
                            ("vision_test", "Проверка зрения"),
                            ("other", "Другое"),
                        ],
                        max_length=30,
                    ),
                ),
                ("test_name", models.CharField(blank=True, max_length=200)),
                ("result", models.TextField()),
                ("performed_date", models.DateField()),
                (
                    "examination",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lab_tests",
                        to="patients.medicalexamination",
                    ),
                ),
                (
                    "file",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="medexam_lab_tests",
                        to="patients.patientfile",
                    ),
                ),
            ],
            options={
                "verbose_name": "Medical Exam Lab Test",
                "verbose_name_plural": "Medical Exam Lab Tests",
                "db_table": "medexam_lab_tests",
                "ordering": ["-performed_date"],
            },
        ),
        # Treatment Plan models
        migrations.CreateModel(
            name="TreatmentPlan",
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
                ("title", models.CharField(max_length=300)),
                ("description", models.TextField(blank=True)),
                ("total_cost", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("total_cost_frozen", models.BooleanField(default=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Черновик"),
                            ("active", "Активный"),
                            ("completed", "Завершен"),
                            ("cancelled", "Отменен"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="treatment_plans",
                        to="patients.patient",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_treatment_plans",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Treatment Plan",
                "verbose_name_plural": "Treatment Plans",
                "db_table": "treatment_plans",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="TreatmentStage",
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
                ("order", models.IntegerField(default=0)),
                ("title", models.CharField(max_length=300)),
                ("description", models.TextField(blank=True)),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Ожидает"),
                            ("in_progress", "В процессе"),
                            ("completed", "Завершен"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stages",
                        to="patients.treatmentplan",
                    ),
                ),
            ],
            options={
                "verbose_name": "Treatment Stage",
                "verbose_name_plural": "Treatment Stages",
                "db_table": "treatment_stages",
                "ordering": ["plan", "order"],
            },
        ),
        migrations.CreateModel(
            name="TreatmentStageItem",
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
                ("description", models.CharField(max_length=500)),
                ("qty_planned", models.DecimalField(decimal_places=2, default=1, max_digits=10)),
                ("qty_completed", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("discount_percent", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("tooth_number", models.CharField(blank=True, max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "stage",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="patients.treatmentstage",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="services.service",
                    ),
                ),
            ],
            options={
                "verbose_name": "Treatment Stage Item",
                "verbose_name_plural": "Treatment Stage Items",
                "db_table": "treatment_stage_items",
                "ordering": ["stage", "id"],
            },
        ),
        migrations.CreateModel(
            name="TreatmentPlanTemplate",
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
                ("name", models.CharField(max_length=300)),
                ("description", models.TextField(blank=True)),
                ("template_data", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="treatment_plan_templates",
                        to="org.organization",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_plan_templates",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Treatment Plan Template",
                "verbose_name_plural": "Treatment Plan Templates",
                "db_table": "treatment_plan_templates",
                "ordering": ["name"],
            },
        ),
        # Add indexes
        migrations.AddIndex(
            model_name="medicalexamination",
            index=models.Index(fields=["patient", "exam_date"], name="medexam_patient_date_idx"),
        ),
        migrations.AddIndex(
            model_name="treatmentplan",
            index=models.Index(fields=["patient", "status"], name="treatment_plan_patient_status_idx"),
        ),
        migrations.AddIndex(
            model_name="treatmentplan",
            index=models.Index(fields=["start_date"], name="treatment_plan_start_date_idx"),
        ),
    ]

