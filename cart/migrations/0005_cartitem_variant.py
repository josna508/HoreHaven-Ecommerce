# Generated by Django 4.2.4 on 2023-09-22 06:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_product_images'),
        ('cart', '0004_remove_cartitem_variant'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='variant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.productvariant'),
        ),
    ]
