# Generated by Django 4.1.7 on 2023-03-24 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_auctions_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctions',
            name='username',
            field=models.CharField(max_length=16),
        ),
    ]
