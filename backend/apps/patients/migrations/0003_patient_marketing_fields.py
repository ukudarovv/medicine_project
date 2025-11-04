# Generated manually for marketing module

from django.contrib.postgres.operations import AddIndexConcurrently
from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0002_patientcontactperson_patientdiagnosis_patientdisease_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=100),
                blank=True,
                default=list,
                help_text='Теги для сегментации (ортодонтия, имплантация и т.д.)',
                size=None
            ),
        ),
        migrations.AddField(
            model_name='patient',
            name='is_marketing_opt_in',
            field=models.BooleanField(
                default=False,
                help_text='Согласие на маркетинговые рассылки'
            ),
        ),
    ]

