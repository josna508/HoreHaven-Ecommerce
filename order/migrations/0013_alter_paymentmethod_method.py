# Generated by Django 4.2.4 on 2023-10-14 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0012_paymentmethod_alter_payment_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethod',
            name='method',
            field=models.CharField(max_length=225),
        ),
    ]
