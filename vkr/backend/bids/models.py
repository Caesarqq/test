from django.db import models
from django.utils import timezone
from lots.models import Lot
from users.models import User


class Bid(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} руб. for {self.lot.title}"


class Transaction(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'В обработке'),
        (STATUS_COMPLETED, 'Завершенный'),
        (STATUS_FAILED, 'Не удалось'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_time = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} руб. for {self.lot.title}"
