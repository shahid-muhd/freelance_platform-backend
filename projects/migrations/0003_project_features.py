# Generated by Django 4.1.13 on 2024-04-19 11:06

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_alter_project_freelancer'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='features',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=115), null=True, size=None),
        ),
    ]
