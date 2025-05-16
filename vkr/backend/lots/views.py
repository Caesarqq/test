from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from rest_framework.generics import (
    CreateAPIView, ListAPIView, RetrieveAPIView, 
    UpdateAPIView, DestroyAPIView, GenericAPIView
)
from rest_framework.views import APIView
import django_filters
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Lot, Category, LotCategory, LotImage, DeliveryDetail
from bids.models import Transaction
from users.models import Notification
from .serializers import (
    LotSerializer, CategorySerializer, LotCategorySerializer,
    LotImageSerializer, DeliveryDetailSerializer
)
from users.permissions import IsOrganization, IsDonor, IsOwner, IsAuctionOwner


class LotFilter(django_filters.FilterSet):
    """
    Фильтр для лотов с возможностью фильтрации по аукциону, категории, цене и статусу.
    """
    auction = django_filters.NumberFilter(field_name='auction', lookup_expr='exact')
    category = django_filters.NumberFilter(field_name='categories')
    min_price = django_filters.NumberFilter(field_name='starting_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='starting_price', lookup_expr='lte')
    status = django_filters.ChoiceFilter(choices=Lot.STATUS_CHOICES)
    
    class Meta:
        model = Lot
        fields = ['auction', 'category', 'min_price', 'max_price', 'status']


class LotCreateView(CreateAPIView):
    """
    Представление для создания лота.
    Только пользователи с ролью 'Донор' могут создавать лоты.
    """
    serializer_class = LotSerializer
    permission_classes = [IsDonor]
    http_method_names = ['post']  # Явно указываем разрешенные HTTP методы
    
    @swagger_auto_schema(
        operation_summary="Создать новый лот",
        operation_description="Создает новый лот для аукциона. Доступно только для пользователей с ролью 'Донор'.",
        request_body=LotSerializer,
        responses={201: LotSerializer, 403: "Недостаточно прав"}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        # Автоматически связываем лот с текущим пользователем как донором
        serializer.save(donor=self.request.user, status=Lot.STATUS_PENDING)


class LotListView(ListAPIView):
    """
    Представление для получения списка всех лотов.
    Доступно для всех пользователей. Можно фильтровать по аукциону.
    """
    queryset = Lot.objects.all()
    serializer_class = LotSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LotFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'starting_price']
    
    @swagger_auto_schema(
        operation_summary="Получить список лотов",
        operation_description="Возвращает список всех лотов с возможностью фильтрации и поиска.",
        manual_parameters=[
            openapi.Parameter(
                'auction', openapi.IN_QUERY, 
                description="Фильтрация по ID аукциона", 
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'category', openapi.IN_QUERY, 
                description="Фильтрация по ID категории", 
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'min_price', openapi.IN_QUERY, 
                description="Минимальная стартовая цена", 
                type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                'max_price', openapi.IN_QUERY, 
                description="Максимальная стартовая цена", 
                type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                'status', openapi.IN_QUERY, 
                description="Статус лота (pending, approved, rejected)", 
                type=openapi.TYPE_STRING, 
                enum=['pending', 'approved', 'rejected']
            ),
            openapi.Parameter(
                'search', openapi.IN_QUERY, 
                description="Поиск по названию и описанию", 
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'ordering', openapi.IN_QUERY, 
                description="Сортировка по полям (created_at, starting_price). Префикс '-' для обратной сортировки", 
                type=openapi.TYPE_STRING
            ),
        ],
        responses={200: LotSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class LotDetailView(RetrieveAPIView):
    """
    Представление для получения деталей конкретного лота.
    Доступно для всех пользователей.
    """
    queryset = Lot.objects.all()
    serializer_class = LotSerializer
    
    @swagger_auto_schema(
        operation_summary="Получить детали лота",
        operation_description="Возвращает детальную информацию о конкретном лоте по его ID.",
        responses={200: LotSerializer, 404: "Лот не найден"}
    )
    def get(self, request, *args, **kwargs):
        lot = self.get_object()
        
        # Проверяем право доступа к лоту на рассмотрении
        if lot.status == 'pending':
            # Доноры могут видеть только свои лоты на рассмотрении
            if request.user.is_authenticated and request.user.role == 'donor' and lot.donor == request.user:
                return super().get(request, *args, **kwargs)
            # Благотворительные организации могут видеть лоты своих аукционов
            if request.user.is_authenticated and request.user.role == 'charity' and hasattr(request.user, 'charity') and lot.auction.charity == request.user.charity:
                return super().get(request, *args, **kwargs)
            # Для всех остальных - лот не найден
            return Response(
                {"detail": "Лот не найден или доступ запрещен"},
                status=status.HTTP_404_NOT_FOUND
            )
        # Для одобренных и проданных лотов доступ есть у всех
        return super().get(request, *args, **kwargs)


class LotUpdateView(UpdateAPIView):
    """
    Представление для обновления лота.
    Только донор-владелец может обновлять лот, и только пока он имеет статус "на рассмотрении".
    """
    queryset = Lot.objects.all()
    serializer_class = LotSerializer
    permission_classes = [IsDonor, IsOwner]
    
    @swagger_auto_schema(
        operation_summary="Обновить лот",
        operation_description="Обновляет информацию о лоте. Доступно только для донора-владельца и только для лотов со статусом 'На рассмотрении'.",
        request_body=LotSerializer,
        responses={
            200: LotSerializer, 
            403: "Недостаточно прав", 
            404: "Лот не найден или не имеет статус 'На рассмотрении'"
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Частично обновить лот",
        operation_description="Частично обновляет информацию о лоте. Доступно только для донора-владельца и только для лотов со статусом 'На рассмотрении'.",
        request_body=LotSerializer,
        responses={
            200: LotSerializer, 
            403: "Недостаточно прав", 
            404: "Лот не найден или не имеет статус 'На рассмотрении'"
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    def get_queryset(self):
        # Только лоты со статусом "на рассмотрении" можно редактировать
        return Lot.objects.filter(donor=self.request.user, status=Lot.STATUS_PENDING)


class LotDeleteView(DestroyAPIView):
    """
    Представление для удаления лота.
    Только донор-владелец может удалять лот и только пока он имеет статус "на рассмотрении".
    """
    queryset = Lot.objects.all()
    serializer_class = LotSerializer
    permission_classes = [IsDonor, IsOwner]
    
    @swagger_auto_schema(
        operation_summary="Удалить лот",
        operation_description="Удаляет лот. Доступно только для донора-владельца и только для лотов со статусом 'На рассмотрении'.",
        responses={204: "Лот успешно удален", 403: "Недостаточно прав", 404: "Лот не найден или не имеет статус 'На рассмотрении'"}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    def get_queryset(self):
        # Доноры могут удалять только свои лоты со статусом "на рассмотрении"
        return Lot.objects.filter(donor=self.request.user, status=Lot.STATUS_PENDING)


class LotStatusUpdateView(GenericAPIView):
    """
    Представление для обновления статуса лота.
    Только организация-владелец аукциона может менять статус.
    """
    queryset = Lot.objects.all()
    serializer_class = LotSerializer
    permission_classes = [IsOrganization, IsAuctionOwner]
    
    @swagger_auto_schema(
        operation_summary="Обновить статус лота",
        operation_description="Обновляет статус лота. Доступно только для организации-владельца аукциона.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['status'],
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=[Lot.STATUS_APPROVED, Lot.STATUS_REJECTED],
                    description="Новый статус лота (approved или rejected)"
                )
            }
        ),
        responses={
            200: LotSerializer, 
            400: "Недопустимый статус", 
            403: "Недостаточно прав", 
            404: "Лот не найден"
        }
    )
    def patch(self, request, *args, **kwargs):
        """
        Обновление статуса лота через PATCH запрос.
        Только организация-владелец аукциона может обновлять статус.
        """
        lot = self.get_object()
        
        # Проверяем права доступа - только организация, владеющая аукционом
        if not hasattr(request.user, 'charity') or lot.auction.charity != request.user.charity:
            return Response(
                {"error": "У вас нет прав на изменение статуса этого лота"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        status_value = request.data.get('status')
        
        # Проверяем, что запрошенный статус допустим
        if status_value not in [Lot.STATUS_APPROVED, Lot.STATUS_REJECTED]:
            return Response(
                {"error": "Недопустимый статус. Разрешены только 'approved' или 'rejected'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lot.status = status_value
        lot.save()
        
        serializer = self.get_serializer(lot)
        return Response(serializer.data)


class LotApproveView(GenericAPIView):
    """
    Представление для одобрения лота.
    Только организация-владелец аукциона может одобрить лот.
    """
    queryset = Lot.objects.all()
    serializer_class = LotSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Одобрить лот",
        operation_description="Одобряет лот. Доступно только для организации-владельца аукциона.",
        responses={
            200: LotSerializer, 
            403: "Недостаточно прав", 
            404: "Лот не найден"
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Одобрение лота через POST запрос.
        Только организация-владелец аукциона может одобрить лот.
        """
        lot = self.get_object()
        
        # Проверяем права доступа - только организация, владеющая аукционом
        if not hasattr(request.user, 'charity') or lot.auction.charity.id != request.user.charity.id:
            return Response(
                {"error": "У вас нет прав на одобрение этого лота"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Устанавливаем статус лота "одобрен"
        lot.status = Lot.STATUS_APPROVED
        lot.save()
        
        # Создаем уведомление для донора
        Notification.objects.create(
            user=lot.donor,
            subject="Ваш лот одобрен",
            message=f"Ваш лот '{lot.title}' был одобрен благотворительной организацией."
        )
        
        serializer = self.get_serializer(lot)
        return Response(serializer.data)


class LotRejectView(GenericAPIView):
    """
    Представление для отклонения лота.
    Только организация-владелец аукциона может отклонить лот.
    """
    queryset = Lot.objects.all()
    serializer_class = LotSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Отклонить лот",
        operation_description="Отклоняет лот. Доступно только для организации-владельца аукциона.",
        responses={
            200: LotSerializer, 
            403: "Недостаточно прав", 
            404: "Лот не найден"
        }
    )
    def post(self, request, *args, **kwargs):
        lot = self.get_object()
        # Удаляем лот при отклонении
        lot.delete()
        return Response({'detail': 'Лот был отклонён и удалён.'}, status=200)


class LotViewSet(viewsets.ModelViewSet):
    queryset = Lot.objects.all()
    serializer_class = LotSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'starting_price']
    
    def get_permissions(self):
        """
        Настройка прав доступа для различных методов:
        - Создание: только для доноров
        - Обновление/удаление: только для владельца-донора
        - Чтение: для всех пользователей
        """
        if self.action == 'create':
            permission_classes = [IsDonor]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsDonor, IsOwner]
        else:
            permission_classes = [permissions.AllowAny]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        # Автоматически связываем лот с текущим пользователем как донором
        serializer.save(donor=self.request.user, status=Lot.STATUS_PENDING)
    
    @swagger_auto_schema(
        operation_summary="Получить лоты по категории",
        operation_description="Возвращает список лотов, относящихся к указанной категории.",
        manual_parameters=[
            openapi.Parameter(
                'category_id', openapi.IN_QUERY, 
                description="ID категории для фильтрации лотов", 
                type=openapi.TYPE_INTEGER, required=True
            ),
        ],
        responses={
            200: LotSerializer(many=True), 
            400: "Отсутствует параметр category_id"
        }
    )
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category_id = request.query_params.get('category_id', None)
        if category_id:
            lots = Lot.objects.filter(categories__id=category_id)
            serializer = self.get_serializer(lots, many=True)
            return Response(serializer.data)
        return Response({"error": "Category ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Получить популярные лоты",
        operation_description="Возвращает список из 10 лотов с наибольшим количеством ставок.",
        responses={200: LotSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def popular(self, request):
        popular_lots = Lot.objects.annotate(
            bid_count=Count('bids')
        ).order_by('-bid_count')[:10]
        serializer = self.get_serializer(popular_lots, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Получить лоты, завершающиеся в ближайшее время",
        operation_description="Возвращает список лотов, аукционы которых завершаются в ближайшие 3 дня.",
        responses={200: LotSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def ending_soon(self, request):
        from django.utils import timezone
        import datetime
        
        today = timezone.now()
        end_date = today + datetime.timedelta(days=3)
        
        ending_soon_lots = Lot.objects.filter(
            auction__end_time__range=[today, end_date],
            auction__status='active'
        )
        serializer = self.get_serializer(ending_soon_lots, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Обновить статус лота",
        operation_description="Обновляет статус лота. Доступно только для организации-владельца аукциона.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['status'],
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=[Lot.STATUS_APPROVED, Lot.STATUS_REJECTED],
                    description="Новый статус лота (approved или rejected)"
                )
            }
        ),
        responses={
            200: LotSerializer, 
            400: "Недопустимый статус", 
            403: "Недостаточно прав", 
            404: "Лот не найден"
        }
    )
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Обновление статуса лота (approve/reject).
        Только организация-владелец аукциона может обновлять статус.
        """
        lot = self.get_object()
        
        # Проверяем права доступа - только организация, владеющая аукционом
        if not hasattr(request.user, 'charity') or lot.auction.charity != request.user.charity:
            return Response(
                {"error": "У вас нет прав на изменение статуса этого лота"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        status_value = request.data.get('status')
        
        # Проверяем, что запрошенный статус допустим
        if status_value not in [Lot.STATUS_APPROVED, Lot.STATUS_REJECTED]:
            return Response(
                {"error": "Недопустимый статус. Разрешены только 'approved' или 'rejected'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lot.status = status_value
        lot.save()
        
        serializer = self.get_serializer(lot)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Получить лоты по аукциону",
        operation_description="Возвращает список лотов, принадлежащих указанному аукциону.",
        manual_parameters=[
            openapi.Parameter(
                'auction_id', openapi.IN_PATH, 
                description="ID аукциона для фильтрации лотов", 
                type=openapi.TYPE_INTEGER, required=True
            ),
        ],
        responses={
            200: LotSerializer(many=True), 
            404: "Аукцион не найден"
        }
    )
    @action(detail=False, url_path=r'auction/(?P<auction_id>\d+)', methods=['get'])
    def by_auction(self, request, auction_id=None):
        """
        Получение списка лотов для конкретного аукциона
        """
        if not auction_id:
            return Response({"error": "Не указан ID аукциона"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Проверка существования аукциона
            from auctions.models import Auction
            auction = get_object_or_404(Auction, pk=auction_id)
            
            # Базовый запрос лотов аукциона
            lots_query = Lot.objects.filter(auction=auction)
            
            # Фильтруем лоты в зависимости от роли пользователя
            # Фильтруем лоты в зависимости от роли пользователя
            if request.user.is_authenticated:
                if request.user.role == 'donor':
                    # Доноры могут видеть свои лоты в любом статусе и все одобренные лоты
                    lots = lots_query.filter(
                        Q(status__in=['approved', 'sold']) | 
                        Q(donor=request.user)  # Это позволяет донору видеть все свои лоты, включая pending
                    )
                elif request.user.role == 'charity' and hasattr(request.user, 'charity') and auction.charity == request.user.charity:
                    # Благотворительная организация-владелец аукциона видит все лоты
                    lots = lots_query
                else:
                    # Обычные пользователи/покупатели видят только одобренные и проданные лоты
                    lots = lots_query.filter(status__in=['approved', 'sold'])
            else:
                # Неавторизованные пользователи видят только одобренные и проданные лоты
                lots = lots_query.filter(status__in=['approved', 'sold'])
            
            serializer = self.get_serializer(lots, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    @swagger_auto_schema(
        operation_summary="Получить список категорий",
        operation_description="Возвращает список всех категорий лотов.",
        responses={200: CategorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Фильтруем в зависимости от роли пользователя
        if request.user.is_authenticated:
            if request.user.role == 'donor':
                queryset = queryset.filter(
                    Q(status__in=['approved', 'sold']) | 
                    Q(status='pending', donor=request.user)
                )
            elif request.user.role == 'charity' and hasattr(request.user, 'charity'):
                queryset = queryset.filter(
                    Q(status__in=['approved', 'sold']) | 
                    Q(auction__charity=request.user.charity)
                )
            else:
                queryset = queryset.filter(status__in=['approved', 'sold'])
        else:
            queryset = queryset.filter(status__in=['approved', 'sold'])
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Получить категорию",
        operation_description="Возвращает информацию о категории по ее ID.",
        responses={200: CategorySerializer, 404: "Категория не найдена"}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class LotCategoryViewSet(viewsets.ModelViewSet):
    queryset = LotCategory.objects.all()
    serializer_class = LotCategorySerializer


class LotImageViewSet(viewsets.ModelViewSet):
    queryset = LotImage.objects.all()
    serializer_class = LotImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'options']


class DeliveryDetailViewSet(viewsets.ModelViewSet):
    queryset = DeliveryDetail.objects.all()
    serializer_class = DeliveryDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Ограничиваем выборку только доставками пользователя
        """
        user = self.request.user
        return DeliveryDetail.objects.filter(transaction__user=user)
    
    @swagger_auto_schema(
        operation_description="Создание информации о доставке",
        request_body=DeliveryDetailSerializer,
        responses={
            201: openapi.Response(
                description="Информация о доставке успешно создана",
                schema=DeliveryDetailSerializer
            ),
            400: "Ошибка при создании информации о доставке",
            404: "Транзакция не найдена"
        },
        tags=['delivery']
    )
    def create(self, request, *args, **kwargs):
        """
        Создание или обновление информации о доставке
        """
        try:
            transaction_id = request.data.get('transaction')
            
            # Проверка существования транзакции
            transaction = get_object_or_404(Transaction, id=transaction_id)
            
            # Проверка прав доступа
            if transaction.user != request.user:
                return Response(
                    {"error": "Вы не можете настроить доставку для чужой покупки"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Проверка статуса транзакции
            if transaction.status != 'completed':
                return Response(
                    {"error": "Невозможно настроить доставку для неоплаченной покупки"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Проверка, существует ли уже информация о доставке
            existing_delivery = DeliveryDetail.objects.filter(transaction=transaction).first()
            
            if existing_delivery:
                # Обновляем существующую запись
                serializer = self.get_serializer(existing_delivery, data=request.data, partial=True)
            else:
                # Создаем новую запись
                serializer = self.get_serializer(data=request.data)
            
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            # Создаем уведомление для донора лота
            Notification.objects.create(
                user=transaction.lot.donor,
                subject="Оформлена доставка для лота",
                message=f"Покупатель оформил доставку для лота '{transaction.lot.title}'."
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Транзакция не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        operation_description="Получение информации о доставке по ID транзакции",
        responses={
            200: openapi.Response(
                description="Информация о доставке",
                schema=DeliveryDetailSerializer
            ),
            404: "Информация о доставке не найдена"
        },
        tags=['delivery']
    )
    @action(detail=False, methods=['get'])
    def by_transaction(self, request):
        """
        Получение информации о доставке по ID транзакции
        """
        transaction_id = request.query_params.get('transaction_id')
        if not transaction_id:
            return Response(
                {"error": "Не указан ID транзакции"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Проверка существования транзакции
            transaction = get_object_or_404(Transaction, id=transaction_id)
            
            # Проверка прав доступа
            if transaction.user != request.user:
                return Response(
                    {"error": "Вы не можете получить информацию о доставке для чужой покупки"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Получение информации о доставке
            delivery = get_object_or_404(DeliveryDetail, transaction=transaction)
            serializer = self.get_serializer(delivery)
            
            return Response(serializer.data)
            
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Транзакция не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        except DeliveryDetail.DoesNotExist:
            return Response(
                {"error": "Информация о доставке не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
