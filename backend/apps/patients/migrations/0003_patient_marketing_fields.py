# Generated manually for marketing module

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0002_patientcontactperson_patientdiagnosis_patientdisease_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='tags',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='Теги для сегментации (ортодонтия, имплантация и т.д.)',
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

