from rest_framework import serializers
from .models import Bid, Transaction
from users.models import Balance
from django.shortcuts import get_object_or_404
from django.db.models import Max
from django.db import transaction


class BidSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    user_email = serializers.ReadOnlyField(source='user.email')
    user_first_name = serializers.ReadOnlyField(source='user.first_name')
    user_last_name = serializers.ReadOnlyField(source='user.last_name')
    
    class Meta:
        model = Bid
        fields = ['id', 'lot', 'user', 'user_username', 'user_email', 'user_first_name', 'user_last_name', 'amount', 'created_at']
        read_only_fields = ['created_at']
    
    def validate(self, data):
        user = data['user']
        lot = data['lot']
        amount = data['amount']
        
        # Правило 1: Ставка должна быть строго больше текущей максимальной ставки на этот лот
        highest_bid = Bid.objects.filter(lot=lot).aggregate(Max('amount'))
        highest_amount = highest_bid['amount__max'] or lot.starting_price
        
        if amount <= highest_amount:
            raise serializers.ValidationError(
                f"Ставка должна быть больше текущей максимальной ставки: {highest_amount} руб."
            )
        
        # Правило 2: Ставка должна быть меньше или равна остатку средств на счёте покупателя
        try:
            balance = get_object_or_404(Balance, user=user)
            if not balance.check_funds(amount):
                raise serializers.ValidationError("Недостаточно средств на счете")
        except Balance.DoesNotExist:
            raise serializers.ValidationError("Баланс пользователя не найден")
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        user = validated_data['user']
        amount = validated_data['amount']
        
        # Списываем средства с баланса
        balance = get_object_or_404(Balance, user=user)
        try:
            balance.withdraw(amount)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        
        # Создаем ставку
        return super().create(validated_data)


class TransactionSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    user_first_name = serializers.ReadOnlyField(source='user.first_name')
    user_last_name = serializers.ReadOnlyField(source='user.last_name')
    lot_title = serializers.ReadOnlyField(source='lot.title')
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'user_username', 'user_first_name', 'user_last_name', 'lot', 'lot_title',
            'amount', 'payment_time', 'payment_method', 'status'
        ]
