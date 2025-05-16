from django.contrib import admin
from .models import Auction, AuctionEvent

# Register your models here.
admin.site.register(Auction)
admin.site.register(AuctionEvent)
