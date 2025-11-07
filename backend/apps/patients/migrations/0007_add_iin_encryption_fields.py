# Generated manually for multi-org consent system

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0006_add_sprint3_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='iin_enc',
            field=models.TextField(blank=True, help_text='Encrypted IIN (AES-256 via Fernet)'),
        ),
        migrations.AddField(
            model_name='patient',
            name='iin_hash',
            field=models.CharField(blank=True, db_index=True, help_text='SHA-256 hash of IIN for lookups', max_length=64),
        ),
        migrations.AlterField(
            model_name='patient',
            name='iin',
            field=models.CharField(blank=True, db_index=True, help_text='ИИН (legacy, use iin_enc for new records)', max_length=20),
        ),
        migrations.AddIndex(
            model_name='patient',
            index=models.Index(fields=['iin_hash'], name='patients_iin_has_7a4e9a_idx'),
        ),
    ]

