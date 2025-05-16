from rest_framework import serializers
from .models import Lot, Category, LotCategory, LotImage, DeliveryDetail


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class LotImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LotImage
        fields = ['id', 'lot', 'image', 'created_at']
        read_only_fields = ['created_at']


class LotCategorySerializer(serializers.ModelSerializer):
    lot_title = serializers.ReadOnlyField(source='lot.title')
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = LotCategory
        fields = ['id', 'lot', 'lot_title', 'category', 'category_name']


class LotSerializer(serializers.ModelSerializer):
    images = LotImageSerializer(many=True, read_only=True)
    donor_username = serializers.ReadOnlyField(source='donor.username')
    donor_first_name = serializers.ReadOnlyField(source='donor.first_name')
    donor_last_name = serializers.ReadOnlyField(source='donor.last_name')
    categories_info = CategorySerializer(source='categories', many=True, read_only=True)
    status_display = serializers.ReadOnlyField(source='get_status_display')
    donor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    auction_charity_id = serializers.SerializerMethodField()
    
    def get_auction_charity_id(self, obj):
        return obj.auction.charity.id if obj.auction and obj.auction.charity else None

    class Meta:
        model = Lot
        fields = [
            'id', 'auction', 'donor', 'donor_username', 'donor_first_name', 'donor_last_name',
            'title', 'description', 'starting_price', 'created_at', 'categories', 'categories_info',
            'images', 'status', 'status_display', 'auction_charity_id'
        ]
        read_only_fields = ['created_at', 'status']


class DeliveryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryDetail
        fields = [
            'id', 'transaction', 'recipient_name', 'address',
            'phone', 'status', 'delivery_type', 'delivery_date', 'created_at'
        ]
        read_only_fields = ['created_at']
