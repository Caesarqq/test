from celery import shared_task
from django.utils import timezone
from django.db.models import Max, OuterRef, Subquery
from django.db import transaction

from .models import Auction, AuctionEvent
from lots.models import Lot
from bids.models import Bid, Transaction
from users.models import Notification, Balance


@shared_task
def process_completed_auctions():
    """
    Задача для обработки завершенных аукционов:
    - Находит аукционы, которые только что завершились
    - Определяет победителей для каждого лота
    - Создает транзакции и уведомления
    """
    now = timezone.now()
    completed_auctions = Auction.objects.filter(
        end_time__lte=now,
        status='active'
    )
    
    if not completed_auctions.exists():
        return "No auctions to process"
    
    processed_auctions = 0
    processed_lots = 0
    
    for auction in completed_auctions:
        with transaction.atomic():
            auction.status = 'completed'
            auction.save()

            AuctionEvent.objects.create(
                auction=auction,
                event_type='auction_ended',
                details=f"Аукцион '{auction.name}' завершен"
            )

            Notification.objects.create(
                user=auction.charity.user,
                subject="Аукцион завершен",
                message=f"Ваш аукцион '{auction.name}' успешно завершен."
            )

            lots = Lot.objects.filter(auction=auction, status='approved')
            
            for lot in lots:
                winning_bid = Bid.objects.filter(lot=lot).order_by('-amount').first()
                
                if winning_bid:
                    lot.status = Lot.STATUS_SOLD
                    lot.winner = winning_bid.user
                    lot.winning_bid_amount = winning_bid.amount
                    lot.save()

                    transaction_obj = Transaction.objects.create(
                        user=winning_bid.user,
                        lot=lot,
                        amount=winning_bid.amount,
                        status='completed',
                        payment_method='balance'
                    )

                    Notification.objects.create(
                        user=winning_bid.user,
                        subject="Вы выиграли лот!",
                        message=f"Поздравляем! Вы выиграли лот '{lot.title}' за {winning_bid.amount} руб. "
                                f"Деньги были списаны с вашего баланса."
                    )

                    Notification.objects.create(
                        user=lot.donor,
                        subject="Ваш лот выигран!",
                        message=f"Ваш лот '{lot.title}' был выигран пользователем {winning_bid.user.username} "
                                f"за {winning_bid.amount} руб."
                    )
                    
                    AuctionEvent.objects.create(
                        auction=auction,
                        lot=lot,
                        event_type='lot_sold',
                        details=f"Лот '{lot.title}' продан пользователю {winning_bid.user.username} за {winning_bid.amount} руб."
                    )

                    other_bids = Bid.objects.filter(lot=lot).exclude(id=winning_bid.id)
                    for bid in other_bids:
                        user_balance = Balance.objects.get(user=bid.user)
                        user_balance.top_up(bid.amount)

                        Notification.objects.create(
                            user=bid.user,
                            subject="Ставка не выиграла",
                            message=f"Ваша ставка на лот '{lot.title}' не выиграла. "
                                    f"Средства в размере {bid.amount} руб. возвращены на ваш баланс."
                        )
                else:
                    lot.status = Lot.STATUS_NOT_SOLD
                    lot.save()

                    AuctionEvent.objects.create(
                        auction=auction,
                        lot=lot,
                        event_type='lot_cancelled',
                        details=f"Лот '{lot.title}' не был продан из-за отсутствия ставок."
                    )

                    Notification.objects.create(
                        user=lot.donor,
                        subject="Лот не продан",
                        message=f"К сожалению, ваш лот '{lot.title}' не был продан. "
                                f"На него не было сделано ни одной ставки."
                    )
                
                processed_lots += 1
        
        processed_auctions += 1
    
    return f"Processed {processed_auctions} auctions and {processed_lots} lots"


@shared_task
def check_auctions_ending_soon():
    """
    Задача для отправки уведомлений об аукционах, которые скоро закончатся
    """
    now = timezone.now()
    ending_soon = now + timezone.timedelta(hours=24)

    auctions = Auction.objects.filter(
        end_time__range=(now, ending_soon),
        status='active'
    )
    
    for auction in auctions:
        lots_with_bids = Lot.objects.filter(
            auction=auction,
            status='approved',
            bids__isnull=False
        ).distinct()
        
        for lot in lots_with_bids:
            bidders = Bid.objects.filter(lot=lot).values_list('user', flat=True).distinct()

            for bidder_id in bidders:
                Notification.objects.create(
                    user_id=bidder_id,
                    subject="Аукцион скоро завершится",
                    message=f"Аукцион '{auction.name}' с лотом '{lot.title}', на который вы сделали ставку, "
                            f"завершится через 24 часа или менее."
                )
    
    return f"Sent notifications for {auctions.count()} auctions ending soon"
