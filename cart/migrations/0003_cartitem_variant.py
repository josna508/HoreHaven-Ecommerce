# Generated by Django 4.2.4 on 2023-09-21 04:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_productvariant'),
        ('cart', '0002_cart_coupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='variant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.productvariant'),
        ),
    ]
