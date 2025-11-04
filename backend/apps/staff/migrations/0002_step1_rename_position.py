# Step 1: Rename old position field to position_legacy
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='position',
            new_name='position_legacy',
        ),
    ]

