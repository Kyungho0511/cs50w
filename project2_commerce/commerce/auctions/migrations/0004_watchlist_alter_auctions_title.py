# Generated by Django 4.1.7 on 2023-03-24 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_rename_bid_start_auctions_starting_price_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='WatchList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32)),
                ('username', models.CharField(max_length=16)),
            ],
        ),
        migrations.AlterField(
            model_name='auctions',
            name='title',
            field=models.CharField(max_length=32),
        ),
    ]