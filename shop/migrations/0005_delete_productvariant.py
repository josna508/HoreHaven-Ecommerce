# Generated by Django 4.2.4 on 2023-09-14 11:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_productvariant_color_code'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProductVariant',
        ),
    ]