# Generated by Django 5.1.1 on 2024-09-23 15:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0006_book'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Book',
        ),
    ]