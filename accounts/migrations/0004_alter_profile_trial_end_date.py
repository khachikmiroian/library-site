# Generated by Django 5.1.1 on 2024-09-12 16:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_profile_first_name_profile_last_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='trial_end_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 15, 16, 2, 26, 527194, tzinfo=datetime.timezone.utc)),
        ),
    ]