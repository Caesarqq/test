from django.db import models
from users.models import User, Charity


class Auction(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Активный'),
        (STATUS_COMPLETED, 'Завершенный'),
        (STATUS_CANCELLED, 'Отмененный'),
    ]
    
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, related_name='auctions')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='auctions/', null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False, verbose_name='Платный аукцион')
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Цена билета')
    
    def __str__(self):
        return self.name


class AuctionTicket(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auction_tickets')
    purchase_date = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('auction', 'user')
        
    def __str__(self):
        return f"Билет для {self.user.email} на аукцион {self.auction.name}"


class AuctionEvent(models.Model):
    EVENT_AUCTION_STARTED = 'auction_started'
    EVENT_LOT_CREATED = 'lot_created'
    EVENT_BID_PLACED = 'bid_placed'
    EVENT_LOT_SOLD = 'lot_sold'
    EVENT_AUCTION_ENDED = 'auction_ended'
    EVENT_LOT_CANCELLED = 'lot_cancelled'
    EVENT_TICKET_PURCHASED = 'ticket_purchased'
    
    EVENT_CHOICES = [
        (EVENT_AUCTION_STARTED, 'Аукцион начался'),
        (EVENT_LOT_CREATED, 'Лот создан'),
        (EVENT_BID_PLACED, 'Ставка сделана'),
        (EVENT_LOT_SOLD, 'Лот продан'),
        (EVENT_AUCTION_ENDED, 'Аукцион завершен'),
        (EVENT_LOT_CANCELLED, 'Лот отменен'),
        (EVENT_TICKET_PURCHASED, 'Билет куплен'),
    ]
    
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='events')
    lot = models.ForeignKey('lots.Lot', on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.auction.name}"
