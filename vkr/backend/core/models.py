from django.db import models
# Импорты для обратной совместимости
from users.models import User, Charity, Notification
from auctions.models import Auction, AuctionEvent
from lots.models import Lot, Category, LotCategory, LotImage, DeliveryDetail
from bids.models import Bid, Transaction
from comments.models import Comment

# Модели перенесены в соответствующие приложения
