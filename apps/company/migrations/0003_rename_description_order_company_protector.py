# Generated by Django 5.1.2 on 2024-11-05 00:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_company_description_company_description_order_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='description_order',
            new_name='protector',
        ),
    ]