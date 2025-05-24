from django.contrib import admin
from .models import Auction, AuctionEvent

admin.site.register(Auction)
admin.site.register(AuctionEvent)
