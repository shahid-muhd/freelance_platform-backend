# Generated by Django 5.0.4 on 2024-05-26 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0010_project_is_advance_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposals',
            name='is_advance_paid',
            field=models.BooleanField(default=False),
        ),
    ]
