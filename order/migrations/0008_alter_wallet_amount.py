# Generated by Django 4.2.4 on 2023-10-03 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0007_alter_wallet_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
