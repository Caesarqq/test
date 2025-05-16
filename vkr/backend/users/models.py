from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserManager(BaseUserManager):
    """Менеджер пользователей для аутентификации по email вместо username"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен для пользователя')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    DONOR = 'donor'
    BUYER = 'buyer'
    CHARITY = 'charity'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (DONOR, 'Донор'),
        (BUYER, 'Покупатель'),
        (CHARITY, 'Благотворительная организация'),
        (ADMIN, 'Администратор'),
    ]
    
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=BUYER)
    is_email_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=20, null=True, blank=True)
    email_verification_expiration = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        # Если username не указан, используем часть email в качестве username
        if not self.username:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)


class Charity(models.Model):
    name = models.CharField(max_length=255)
    ogrn = models.CharField(max_length=13, unique=True, null=True, blank=True, verbose_name='ОГРН')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Charities"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.subject} for {self.user.email}"


class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='balance')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Баланс {self.user.email}: {self.amount} руб."
    
    def top_up(self, amount):
        """Пополнение баланса"""
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self.amount += amount
        self.save()
        return self.amount
    
    def withdraw(self, amount):
        """Списание средств с баланса"""
        if amount <= 0:
            raise ValueError("Сумма списания должна быть положительной")
        if self.amount < amount:
            raise ValueError("Недостаточно средств на счете")
        self.amount -= amount
        self.save()
        return self.amount
    
    def check_funds(self, amount):
        """Проверка достаточности средств"""
        return self.amount >= amount


# Сигнал для создания баланса и charity при регистрации пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Создаем баланс для всех пользователей
        Balance.objects.create(user=instance)
        
        # Если пользователь имеет роль charity, создаем запись в таблице Charity
        if instance.role == 'charity':
            # Получаем имя из email или user.username
            charity_name = instance.first_name or instance.username or instance.email.split('@')[0]
            Charity.objects.create(
                user=instance,
                name=f"Благотворительная организация {charity_name}",
                description=f"Автоматически созданная организация для пользователя {instance.email}",
                ogrn=None
            )
