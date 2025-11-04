# Generated manually for Sprint 4

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("billing", "0003_initial"),
        ("org", "0001_initial"),
        ("patients", "0006_add_sprint3_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Extend Payment model with KZ fields
        migrations.AddField(
            model_name="payment",
            name="qr_code_url",
            field=models.URLField(blank=True, help_text="URL for QR code image (Kaspi QR)"),
        ),
        migrations.AddField(
            model_name="payment",
            name="redirect_url",
            field=models.URLField(blank=True, help_text="Redirect URL for payment page (Halyk Pay)"),
        ),
        migrations.AddField(
            model_name="payment",
            name="callback_data",
            field=models.JSONField(blank=True, default=dict, help_text="Callback data from provider"),
        ),
        # Update ext_id help text
        migrations.AlterField(
            model_name="payment",
            name="ext_id",
            field=models.CharField(blank=True, max_length=200, help_text="External payment ID from provider"),
        ),
        # PaymentProvider model
        migrations.CreateModel(
            name="PaymentProvider",
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
                    "provider_type",
                    models.CharField(
                        choices=[
                            ("kaspi", "Kaspi QR"),
                            ("halyk", "Halyk Pay"),
                            ("paybox", "Paybox"),
                        ],
                        max_length=20,
                    ),
                ),
                ("merchant_id", models.CharField(max_length=200)),
                ("api_key", models.CharField(max_length=500)),
                ("api_secret", models.CharField(blank=True, max_length=500)),
                ("webhook_url", models.URLField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_test_mode", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_providers",
                        to="org.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Payment Provider",
                "verbose_name_plural": "Payment Providers",
                "db_table": "payment_providers",
            },
        ),
        # TaxDeductionCertificate model
        migrations.CreateModel(
            name="TaxDeductionCertificate",
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
                ("year", models.IntegerField()),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("services_list", models.JSONField(default=list)),
                ("certificate_number", models.CharField(max_length=50, unique=True)),
                ("issued_date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Черновик"),
                            ("issued", "Выдана"),
                            ("cancelled", "Отменена"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tax_certificates",
                        to="patients.patient",
                    ),
                ),
                (
                    "issued_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="issued_tax_certificates",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Tax Deduction Certificate",
                "verbose_name_plural": "Tax Deduction Certificates",
                "db_table": "tax_deduction_certificates",
                "ordering": ["-issued_date"],
            },
        ),
        # Add indexes
        migrations.AddIndex(
            model_name="taxdeductioncertificate",
            index=models.Index(fields=["patient", "year"], name="tax_cert_patient_year_idx"),
        ),
        migrations.AddIndex(
            model_name="taxdeductioncertificate",
            index=models.Index(fields=["certificate_number"], name="tax_cert_number_idx"),
        ),
        # Add unique constraint
        migrations.AlterUniqueTogether(
            name="paymentprovider",
            unique_together={("organization", "provider_type")},
        ),
    ]

