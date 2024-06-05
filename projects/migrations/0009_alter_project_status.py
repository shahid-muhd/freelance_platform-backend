# Generated by Django 5.0.4 on 2024-05-17 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_project_is_archived'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(choices=[('recruiting', 'Recruiting'), ('progressing', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('hold', 'On Hold')], default='recruiting', max_length=20),
        ),
    ]
