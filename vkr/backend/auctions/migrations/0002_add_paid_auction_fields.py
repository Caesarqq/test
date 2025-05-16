from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='is_paid',
            field=models.BooleanField(default=False, verbose_name='Платный аукцион'),
        ),
        migrations.AddField(
            model_name='auction',
            name='ticket_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Цена билета'),
        ),
        migrations.CreateModel(
            name='AuctionTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchase_date', models.DateTimeField(auto_now_add=True)),
                ('is_used', models.BooleanField(default=False)),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='auctions.auction')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auction_tickets', to='users.user')),
            ],
            options={
                'unique_together': {('auction', 'user')},
            },
        ),
    ] 