# Generated by Django 5.1.1 on 2024-10-08 13:07

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_purchaser'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaser',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
