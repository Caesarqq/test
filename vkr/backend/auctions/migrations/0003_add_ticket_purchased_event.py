from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_add_paid_auction_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionevent',
            name='event_type',
            field=models.CharField(
                choices=[
                    ('auction_started', 'Аукцион начался'),
                    ('lot_created', 'Лот создан'),
                    ('bid_placed', 'Ставка сделана'),
                    ('lot_sold', 'Лот продан'),
                    ('auction_ended', 'Аукцион завершен'),
                    ('lot_cancelled', 'Лот отменен'),
                    ('ticket_purchased', 'Билет куплен')
                ],
                max_length=20
            ),
        ),
    ] 