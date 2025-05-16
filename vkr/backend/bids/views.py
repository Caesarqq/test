from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Max
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Bid, Transaction
from .serializers import BidSerializer, TransactionSerializer
from lots.models import Lot, DeliveryDetail
from users.models import Notification, Balance, User
from auctions.models import AuctionEvent


class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    
    @swagger_auto_schema(
        operation_description="Создание новой ставки на лот",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['lot', 'amount'],
            properties={
                'lot': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID лота'),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Сумма ставки')
            }
        ),
        responses={
            201: openapi.Response(
                description="Ставка успешно создана",
                schema=BidSerializer
            ),
            400: "Ошибка при создании ставки",
            404: "Лот не найден"
        },
        tags=['bids']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Получаем данные из запроса
        lot_id = request.data.get('lot')
        user_id = request.user.id
        amount = float(request.data.get('amount'))
        
        # Проверяем, существует ли лот
        try:
            lot = Lot.objects.get(id=lot_id)
        except Lot.DoesNotExist:
            return Response({"error": "Lot not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Проверяем, что лот одобрен
        if lot.status != Lot.STATUS_APPROVED:
            return Response({"error": "Лот не одобрен для участия в аукционе"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем, активен ли аукцион
        if lot.auction.status != 'active':
            return Response({"error": "Auction is not active"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем, закончился ли аукцион
        from django.utils import timezone
        if lot.auction.end_time < timezone.now():
            return Response({"error": "Auction has ended"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем, что пользователь не является донором лота
        if lot.donor.id == user_id:
            return Response({"error": "Вы не можете делать ставки на собственный лот"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем, что пользователь имеет роль покупателя
        user = User.objects.get(id=user_id)
        if user.role != User.BUYER:
            return Response({"error": "Только пользователи с ролью 'Покупатель' могут делать ставки"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Находим текущую максимальную ставку
        highest_bid = Bid.objects.filter(lot=lot).aggregate(Max('amount'))
        highest_amount = highest_bid['amount__max'] or lot.starting_price
        
        # Проверяем, достаточно ли высока новая ставка
        if amount <= highest_amount:
            return Response(
                {"error": f"Bid amount must be higher than current highest bid: {highest_amount}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем, достаточно ли средств на балансе пользователя
        try:
            balance = Balance.objects.select_for_update().get(user_id=user_id)
            if balance.amount < amount:
                return Response(
                    {"error": "Insufficient funds in your balance"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Balance.DoesNotExist:
            return Response(
                {"error": "User balance not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создаем новую ставку
        serializer = self.get_serializer(data={
            'lot': lot_id,
            'user': user_id,
            'amount': amount
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Списываем средства с баланса пользователя уже выполнено в сериализаторе
        
        # Создаем событие аукциона
        AuctionEvent.objects.create(
            auction=lot.auction,
            lot=lot,
            event_type='bid_placed',
            details=f"Пользователь {request.user.username} сделал ставку {amount} руб."
        )
        
        # Создаем уведомление для донора лота
        Notification.objects.create(
            user=lot.donor,
            subject="Новая ставка на ваш лот",
            message=f"На ваш лот '{lot.title}' была сделана новая ставка: {amount} руб."
        )
        
        # Если есть предыдущий лидер ставок, возвращаем ему деньги
        previous_highest_bid = Bid.objects.filter(lot=lot).exclude(id=serializer.instance.id).order_by('-amount').first()
        if previous_highest_bid:
            previous_user_balance = Balance.objects.get(user=previous_highest_bid.user)
            previous_user_balance.top_up(previous_highest_bid.amount)
            
            # Создаем уведомление для предыдущего лидера
            Notification.objects.create(
                user=previous_highest_bid.user,
                subject="Ваша ставка перебита",
                message=f"Ваша ставка на лот '{lot.title}' была перебита. Средства в размере {previous_highest_bid.amount} руб. возвращены на ваш баланс."
            )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_description="Получение списка ставок текущего пользователя",
        responses={
            200: openapi.Response(
                description="Список ставок пользователя",
                schema=BidSerializer(many=True)
            )
        },
        tags=['bids']
    )
    @action(detail=False, methods=['get'])
    def my_bids(self, request):
        bids = Bid.objects.filter(user=request.user).order_by('-created_at')
        serializer = self.get_serializer(bids, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Получение списка ставок для конкретного лота",
        responses={
            200: openapi.Response(
                description="Список ставок на лот",
                schema=BidSerializer(many=True)
            ),
            404: "Лот не найден"
        },
        tags=['bids']
    )
    @action(detail=False, methods=['get'])
    def by_lot(self, request):
        lot_id = request.query_params.get('lot_id')
        if not lot_id:
            return Response({"error": "lot_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            Lot.objects.get(id=lot_id)
        except Lot.DoesNotExist:
            return Response({"error": "Lot not found"}, status=status.HTTP_404_NOT_FOUND)
            
        bids = Bid.objects.filter(lot_id=lot_id).order_by('-amount')
        serializer = self.get_serializer(bids, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Оплата выигранного лота",
        responses={
            200: openapi.Response(
                description="Оплата успешно произведена",
                schema=TransactionSerializer
            ),
            400: "Ошибка при оплате",
            404: "Ставка не найдена"
        },
        tags=['bids']
    )
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def pay(self, request, pk=None):
        """
        Оплата выигранного лота
        """
        try:
            bid = get_object_or_404(Bid, id=pk)
            
            # Отладочное логирование
            print(f"Processing payment for bid ID={pk}, lot ID={bid.lot.id}, status={bid.lot.status}")
            
            # Проверка, что пользователь является владельцем ставки
            if bid.user != request.user:
                print(f"Payment rejected: user {request.user.id} is not the owner of bid {pk}")
                return Response(
                    {"error": "Вы не можете оплатить чужую ставку"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Проверка, что нет существующих транзакций для этого лота от этого пользователя
            existing_transaction = Transaction.objects.filter(
                lot=bid.lot, 
                user=request.user, 
                status='completed'
            ).first()
            
            if existing_transaction:
                print(f"Payment rejected: existing transaction {existing_transaction.id} found")
                
                # Проверяем, есть ли данные о доставке для этой транзакции
                delivery_exists = DeliveryDetail.objects.filter(transaction=existing_transaction).exists()
                
                # Если доставка не оформлена, не считаем лот оплаченным
                if not delivery_exists:
                    print(f"Delivery details not found for transaction {existing_transaction.id}, returning transaction without marking as paid")
                    return Response(
                        TransactionSerializer(existing_transaction).data
                    )
                
                return Response(
                    {"error": "Лот уже оплачен"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Проверка баланса пользователя
            balance = get_object_or_404(Balance, user=request.user)
            if balance.amount < bid.amount:
                print(f"Payment rejected: insufficient funds. Balance: {balance.amount}, Required: {bid.amount}")
                return Response(
                    {"error": "Недостаточно средств на балансе"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Создание транзакции
            transaction = Transaction.objects.create(
                user=request.user,
                lot=bid.lot,
                amount=bid.amount,
                payment_method='balance',  # По умолчанию используем баланс
                status='pending'
            )
            
            # Списание средств
            balance.withdraw(bid.amount)
            
            # Обновление статуса транзакции
            transaction.status = 'completed'
            transaction.save()
            
            # Статус лота обновляется только при наличии информации о доставке
            # Обновление статуса лота происходит при сохранении информации о доставке
            
            print(f"Payment successful: transaction {transaction.id} created")
            
            # Создаем уведомление для донора лота
            Notification.objects.create(
                user=bid.lot.donor,
                subject="Оплата за ваш лот",
                message=f"Ваш лот '{bid.lot.title}' был оплачен пользователем {request.user.username} за {bid.amount} руб. Ожидаем информацию о доставке."
            )
            
            # Создаем уведомление для победителя
            Notification.objects.create(
                user=request.user,
                subject="Оплата произведена успешно",
                message=f"Вы успешно оплатили лот '{bid.lot.title}'. Пожалуйста, заполните информацию о доставке."
            )
            
            # Возвращаем данные созданной транзакции
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data)
            
        except Bid.DoesNotExist:
            print(f"Payment rejected: bid {pk} not found")
            return Response(
                {"error": "Ставка не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Payment error: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        operation_description="Подтверждение получения лота",
        responses={
            200: openapi.Response(
                description="Получение подтверждено",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            400: "Ошибка при подтверждении",
            404: "Ставка не найдена"
        },
        tags=['bids']
    )
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def confirm_delivery(self, request, pk=None):
        """
        Подтверждение получения выигранного лота
        """
        try:
            bid = get_object_or_404(Bid, id=pk)
            
            # Проверка, что пользователь является владельцем ставки
            if bid.user != request.user:
                return Response(
                    {"error": "Вы не можете подтвердить получение чужого лота"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Проверка, что лот оплачен и отправлен
            transaction = Transaction.objects.filter(
                lot=bid.lot, 
                user=request.user, 
                status='completed'
            ).first()
            
            if not transaction:
                return Response(
                    {"error": "Лот не был оплачен"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Проверка статуса доставки
            try:
                delivery = DeliveryDetail.objects.get(transaction=transaction)
                if delivery.status != DeliveryDetail.STATUS_SHIPPED:
                    return Response(
                        {"error": "Лот еще не отправлен"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Обновление статуса доставки
                delivery.status = DeliveryDetail.STATUS_DELIVERED
                delivery.save()
                
                # Создаем уведомление для донора лота
                Notification.objects.create(
                    user=bid.lot.donor,
                    subject="Доставка лота подтверждена",
                    message=f"Покупатель подтвердил получение лота '{bid.lot.title}'."
                )
                
                # Создаем уведомление для победителя
                Notification.objects.create(
                    user=request.user,
                    subject="Спасибо за подтверждение доставки!",
                    message=f"Вы подтвердили получение лота '{bid.lot.title}'. Спасибо за участие в благотворительном аукционе!"
                )
                
                return Response({
                    "message": "Получение лота успешно подтверждено",
                    "delivery_status": "delivered"
                })
                
            except DeliveryDetail.DoesNotExist:
                return Response(
                    {"error": "Информация о доставке не найдена"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except Bid.DoesNotExist:
            return Response(
                {"error": "Ставка не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    
    @swagger_auto_schema(
        operation_description="Получение списка завершенных покупок пользователя",
        responses={
            200: openapi.Response(
                description="Список транзакций",
                schema=TransactionSerializer(many=True)
            )
        },
        tags=['transactions']
    )
    @action(detail=False, methods=['get'])
    def my_purchases(self, request):
        transactions = Transaction.objects.filter(
            user=request.user,
            status='completed'
        )
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
