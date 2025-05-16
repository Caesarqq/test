from django.db import models
from auctions.models import Auction
from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"


class Lot(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_SOLD = 'sold'
    STATUS_NOT_SOLD = 'not_sold'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'На рассмотрении'),
        (STATUS_APPROVED, 'Одобрен'),
        (STATUS_REJECTED, 'Отклонён'),
        (STATUS_SOLD, 'Продан'),
        (STATUS_NOT_SOLD, 'Не продан'),
    ]
    
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='lots')
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donated_lots')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='LotCategory')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='won_lots', null=True, blank=True)
    winning_bid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return self.title


class LotCategory(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.lot.title} - {self.category.name}"
    
    class Meta:
        verbose_name_plural = "Lot Categories"


class LotImage(models.Model):
    lot = models.ForeignKey(
        Lot,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='lot_images/',
        null=True,    # ← сюда
        blank=True    # ← и сюда
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.lot.title}"


class DeliveryDetail(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_FAILED = 'failed'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидает отправки'),
        (STATUS_SHIPPED, 'Отправлено'),
        (STATUS_DELIVERED, 'Доставлено'),
        (STATUS_FAILED, 'Не удалось доставить'),
    ]
    
    DELIVERY_TYPE_COURIER = 'courier'
    DELIVERY_TYPE_PICKUP = 'pickup'
    
    DELIVERY_TYPE_CHOICES = [
        (DELIVERY_TYPE_COURIER, 'Курьером'),
        (DELIVERY_TYPE_PICKUP, 'Самовывоз'),
    ]
    
    transaction = models.OneToOneField('bids.Transaction', on_delete=models.CASCADE, related_name='delivery')
    recipient_name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_TYPE_CHOICES, default=DELIVERY_TYPE_COURIER)
    delivery_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Delivery for {self.transaction.lot.title} to {self.recipient_name}"
