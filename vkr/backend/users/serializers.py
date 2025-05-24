from rest_framework import serializers
from .models import User, Charity, Notification, Balance
import secrets
import string
from django.utils import timezone
from datetime import timedelta
from .models import Subscription

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_email_verified']
        read_only_fields = ['is_email_verified']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role', 'is_email_verified', 'date_joined']
        read_only_fields = ['id', 'email', 'date_joined', 'is_email_verified']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'password']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    ogrn = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'password', 'password_confirm', 'ogrn']
        
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        if data.get('role') == 'charity':
            ogrn = data.get('ogrn', '')
            if not ogrn or not ogrn.isdigit() or len(ogrn) != 13:
                raise serializers.ValidationError({'ogrn': 'ОГРН должен содержать ровно 13 цифр'})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        ogrn = validated_data.pop('ogrn', None)
        if validated_data.get('role') == 'charity':
            validated_data.pop('last_name', None)
        else:
            ogrn = None
        user = User(**validated_data)
        user.set_password(password)
        user.is_email_verified = False
        verification_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
        user.email_verification_code = verification_code
        user.email_verification_expiration = timezone.now() + timedelta(days=1)
        user.save()
        if user.role == 'charity' and ogrn:
            charity = Charity.objects.filter(user=user).first()
            if charity:
                charity.ogrn = ogrn
                charity.save()
        return user


class CharitySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Charity
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['user']


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ['id', 'user', 'amount', 'updated_at']
        read_only_fields = ['id', 'user', 'amount', 'updated_at']


class TopUpBalanceSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Сумма пополнения должна быть положительной")
        return value
    
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'is_active', 'start_date', 'end_date', 'auto_renewal']
        read_only_fields = ['id', 'start_date']