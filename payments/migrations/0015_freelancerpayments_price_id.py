# Generated by Django 5.0.4 on 2024-05-24 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0014_alter_freelancerpayments_invoice_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='freelancerpayments',
            name='price_id',
            field=models.CharField(default='ddfgfgr', max_length=155),
            preserve_default=False,
        ),
    ]