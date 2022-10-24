# Generated by Django 4.1.1 on 2022-10-19 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_alter_bid_bid_amount_alter_listing_starting_bid'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='watchlist',
            field=models.ManyToManyField(blank=True, related_name='watchlist', to='auctions.listing'),
        ),
        migrations.AddField(
            model_name='user',
            name='watchlist_counter',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
