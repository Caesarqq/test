from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import (
    CreateAPIView, ListAPIView, RetrieveAPIView, 
    UpdateAPIView, DestroyAPIView
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Auction, AuctionEvent, AuctionTicket
from .serializers import AuctionSerializer, AuctionEventSerializer, AuctionTicketSerializer
from users.permissions import IsOrganization, IsOwner, IsAuctionOwner
from users.models import Balance



class AuctionCreateView(CreateAPIView):
    """
    Представление для создания аукциона.
    Только пользователи с ролью 'Организация' могут создавать аукционы.
    """
    serializer_class = AuctionSerializer
    permission_classes = [IsOrganization]
    
    @swagger_auto_schema(
        operation_summary="Создать новый аукцион",
        operation_description="Создает новый аукцион. Доступно только для пользователей с ролью 'Организация'.",
        responses={201: AuctionSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(charity=self.request.user.charity)


class AuctionListView(ListAPIView):
    """
    Представление для получения списка всех аукционов.
    Доступно для всех пользователей.
    """
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'start_time', 'end_time']
    
    @swagger_auto_schema(
        operation_summary="Получить список аукционов",
        operation_description="Возвращает список всех аукционов. Поддерживает поиск и сортировку.",
        manual_parameters=[
            openapi.Parameter(
                'search', openapi.IN_QUERY, 
                description="Поиск по имени и описанию", 
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'ordering', openapi.IN_QUERY, 
                description="Сортировка по полям (created_at, start_time, end_time). Префикс '-' для обратной сортировки", 
                type=openapi.TYPE_STRING
            ),
        ],
        responses={200: AuctionSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context




class AuctionUpdateView(UpdateAPIView):
    """
    Представление для обновления аукциона.
    Только организация-владелец может обновлять аукцион.
    """
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    permission_classes = [IsOrganization, IsAuctionOwner]
    
    @swagger_auto_schema(
        operation_summary="Обновить аукцион",
        operation_description="Обновляет информацию об аукционе. Доступно только для организации-владельца.",
        responses={200: AuctionSerializer, 403: "Недостаточно прав", 404: "Аукцион не найден"}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Частично обновить аукцион",
        operation_description="Частично обновляет информацию об аукционе. Доступно только для организации-владельца.",
        responses={200: AuctionSerializer, 403: "Недостаточно прав", 404: "Аукцион не найден"}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class AuctionDeleteView(DestroyAPIView):
    """
    Представление для удаления аукциона.
    Только организация-владелец может удалять аукцион.
    """
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    permission_classes = [IsOrganization, IsAuctionOwner]
    
    @swagger_auto_schema(
        operation_summary="Удалить аукцион",
        operation_description="Удаляет аукцион. Доступно только для организации-владельца.",
        responses={204: "Аукцион успешно удален", 403: "Недостаточно прав", 404: "Аукцион не найден"}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def get_permissions(self):
        """
        Настройка прав доступа для различных методов:
        - Создание: только для организаций
        - Обновление/удаление: только для владельца-организации
        - Чтение: для всех пользователей
        """
        if self.action == 'create':
            permission_classes = [IsOrganization]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOrganization, IsAuctionOwner]
        else:
            permission_classes = [permissions.AllowAny]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(charity=self.request.user.charity)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @swagger_auto_schema(
        operation_summary="Получить активные аукционы",
        operation_description="Возвращает список всех активных аукционов.",
        responses={200: AuctionSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        active_auctions = Auction.objects.filter(status='active')
        serializer = self.get_serializer(active_auctions, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Получить завершенные аукционы",
        operation_description="Возвращает список всех завершенных аукционов.",
        responses={200: AuctionSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def completed(self, request):
        completed_auctions = Auction.objects.filter(status='completed')
        serializer = self.get_serializer(completed_auctions, many=True)
        return Response(serializer.data)


class AuctionEventViewSet(viewsets.ModelViewSet):
    queryset = AuctionEvent.objects.all()
    serializer_class = AuctionEventSerializer
    
    @swagger_auto_schema(
        operation_summary="Получить события аукциона",
        operation_description="Возвращает список событий для конкретного аукциона.",
        manual_parameters=[
            openapi.Parameter(
                'auction_id', openapi.IN_QUERY, 
                description="ID аукциона для фильтрации событий", 
                type=openapi.TYPE_INTEGER, required=True
            ),
        ],
        responses={
            200: AuctionEventSerializer(many=True), 
            400: "Отсутствует параметр auction_id"
        }
    )
    @action(detail=False, methods=['get'])
    def by_auction(self, request):
        auction_id = request.query_params.get('auction_id', None)
        if auction_id:
            events = AuctionEvent.objects.filter(auction_id=auction_id).order_by('-created_at')
            serializer = self.get_serializer(events, many=True)
            return Response(serializer.data)
        return Response({"error": "Auction ID is required"}, status=status.HTTP_400_BAD_REQUEST)

class AuctionDetailView(RetrieveAPIView):
    """
    Представление для получения информации об отдельном аукционе.
    Доступно для всех пользователей.
    """
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Получить детали аукциона",
        operation_description="Возвращает подробную информацию об аукционе по его ID.",
        responses={200: AuctionSerializer, 404: "Аукцион не найден"}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
class AuctionTicketViewSet(viewsets.ModelViewSet):
    queryset = AuctionTicket.objects.all()
    serializer_class = AuctionTicketSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        
        return [permission() for permission in permission_classes]
    
    @swagger_auto_schema(
        operation_summary="Купить билет на аукцион",
        operation_description="Позволяет пользователю купить билет на платный аукцион.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['auction'],
            properties={
                'auction': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID аукциона')
            }
        ),
        responses={
            201: AuctionTicketSerializer,
            400: "Неверные данные или нет средств на балансе",
            403: "Недостаточно прав",
            404: "Аукцион не найден"
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def purchase(self, request):
        auction_id = request.data.get('auction')
        if not auction_id:
            return Response({"error": "Необходимо указать ID аукциона"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            auction = Auction.objects.get(pk=auction_id)
        except Auction.DoesNotExist:
            return Response({"error": "Аукцион не найден"}, status=status.HTTP_404_NOT_FOUND)

        if not auction.is_paid:
            return Response({"error": "Этот аукцион бесплатный, билет не требуется"}, status=status.HTTP_400_BAD_REQUEST)

        if AuctionTicket.objects.filter(auction=auction, user=request.user).exists():
            return Response({"error": "У вас уже есть билет на этот аукцион"}, status=status.HTTP_400_BAD_REQUEST)

        user_balance = Balance.objects.get(user=request.user)
        if not user_balance.check_funds(auction.ticket_price):
            return Response({"error": "Недостаточно средств на балансе"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_balance.withdraw(auction.ticket_price)
            ticket = AuctionTicket.objects.create(
                auction=auction,
                user=request.user
            )

            AuctionEvent.objects.create(
                auction=auction,
                event_type=AuctionEvent.EVENT_TICKET_PURCHASED,
                details=f"Пользователь {request.user.email} купил билет на аукцион"
            )
            
            serializer = self.get_serializer(ticket)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="Проверить наличие билета",
        operation_description="Проверяет, есть ли у пользователя билет на указанный аукцион.",
        manual_parameters=[
            openapi.Parameter(
                'auction_id', openapi.IN_QUERY, 
                description="ID аукциона для проверки билета", 
                type=openapi.TYPE_INTEGER, required=True
            ),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'has_ticket': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'ticket': AuctionTicketSerializer()
                }
            ),
            400: "Неверные данные",
            404: "Аукцион не найден"
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def check_access(self, request):
        auction_id = request.query_params.get('auction_id')
        if not auction_id:
            return Response({"error": "Необходимо указать ID аукциона"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            auction = Auction.objects.get(pk=auction_id)
        except Auction.DoesNotExist:
            return Response({"error": "Аукцион не найден"}, status=status.HTTP_404_NOT_FOUND)

        if not auction.is_paid:
            return Response({"has_ticket": True, "ticket": None}, status=status.HTTP_200_OK)

        if hasattr(request.user, 'charity') and request.user.charity.id == auction.charity.id:
            return Response({"has_ticket": True, "ticket": None}, status=status.HTTP_200_OK)

        if request.user.role == 'donor':
            return Response({"has_ticket": True, "ticket": None}, status=status.HTTP_200_OK)

        from django.utils import timezone
        from users.models import Subscription
        
        active_subscription = Subscription.objects.filter(
            user=request.user,
            is_active=True,
            end_date__gt=timezone.now()
        ).exists()
        
        if active_subscription:
            return Response({"has_ticket": True, "ticket": None}, status=status.HTTP_200_OK)

        try:
            ticket = AuctionTicket.objects.get(auction=auction, user=request.user)
            serializer = self.get_serializer(ticket)
            return Response({"has_ticket": True, "ticket": serializer.data}, status=status.HTTP_200_OK)
        except AuctionTicket.DoesNotExist:
            return Response({"has_ticket": False, "ticket": None}, status=status.HTTP_200_OK)