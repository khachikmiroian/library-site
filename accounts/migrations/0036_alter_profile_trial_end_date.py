# Generated by Django 5.1.1 on 2024-09-23 15:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0035_alter_profile_trial_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='trial_end_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 26, 15, 51, 43, 958640, tzinfo=datetime.timezone.utc)),
        ),
    ]
