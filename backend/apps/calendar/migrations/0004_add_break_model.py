# Generated manually on 2025-11-05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),
        ('calendar', '0003_add_waitlist'),
    ]

    operations = [
        migrations.CreateModel(
            name='Break',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('break_type', models.CharField(
                    choices=[
                        ('lunch', 'Обед'),
                        ('break', 'Перерыв'),
                        ('meeting', 'Совещание'),
                        ('other', 'Другое')
                    ],
                    default='break',
                    max_length=20
                )),
                ('date', models.DateField(db_index=True)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('note', models.TextField(blank=True, help_text='Примечание к перерыву')),
                ('is_recurring', models.BooleanField(default=False, help_text='Повторяется каждый день')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='breaks', to='staff.employee')),
            ],
            options={
                'verbose_name': 'Break',
                'verbose_name_plural': 'Breaks',
                'db_table': 'breaks',
                'ordering': ['date', 'start_time'],
            },
        ),
        migrations.AddIndex(
            model_name='break',
            index=models.Index(fields=['employee', 'date'], name='breaks_employe_idx'),
        ),
        migrations.AddIndex(
            model_name='break',
            index=models.Index(fields=['date', 'start_time'], name='breaks_date_idx'),
        ),
    ]

