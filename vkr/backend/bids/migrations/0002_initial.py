# Generated by Django 5.2 on 2025-05-15 15:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bids', '0001_initial'),
        ('lots', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='lot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='lots.lot'),
        ),
    ]
