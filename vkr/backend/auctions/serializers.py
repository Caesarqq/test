from rest_framework import serializers
from .models import Auction, AuctionEvent, AuctionTicket


class AuctionSerializer(serializers.ModelSerializer):
    charity_name = serializers.ReadOnlyField(source='charity.name')
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Auction
        fields = [
            'id', 'charity', 'charity_name', 'name', 'description',
            'start_time', 'end_time', 'status', 'created_at', 'image', 'image_url',
            'is_paid', 'ticket_price'
        ]
        read_only_fields = ['created_at']
        
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class AuctionTicketSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    auction_name = serializers.ReadOnlyField(source='auction.name')
    
    class Meta:
        model = AuctionTicket
        fields = [
            'id', 'auction', 'auction_name', 'user', 'user_email',
            'purchase_date', 'is_used'
        ]
        read_only_fields = ['purchase_date', 'is_used']


class AuctionEventSerializer(serializers.ModelSerializer):
    auction_name = serializers.ReadOnlyField(source='auction.name')
    lot_title = serializers.ReadOnlyField(source='lot.title')
    event_type_display = serializers.ReadOnlyField(source='get_event_type_display')
    
    class Meta:
        model = AuctionEvent
        fields = [
            'id', 'auction', 'auction_name', 'lot', 'lot_title',
            'event_type', 'event_type_display', 'details', 'created_at'
        ]
        read_only_fields = ['created_at']
