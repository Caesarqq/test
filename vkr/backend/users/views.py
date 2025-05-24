from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import timedelta
from .models import Subscription

from .models import User, Charity, Notification, Balance
from .serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    CharitySerializer, 
    NotificationSerializer,
    RegisterSerializer,
    ProfileSerializer,
    BalanceSerializer,
    TopUpBalanceSerializer
)
from .tasks import send_verification_email


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_email_verified:
            raise AuthenticationFailed('Аккаунт не подтвержден. Пожалуйста, проверьте вашу почту и подтвердите регистрацию.')
        data['user_id'] = self.user.id
        data['email'] = self.user.email
        data['role'] = self.user.role
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        data['unread_notifications_count'] = Notification.objects.filter(
            user=instance, 
            is_read=False
        ).count()
        
        return Response(data)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        pk = self.kwargs.get('pk')
        if pk == 'me':
            return self.request.user
        return super().get_object()


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        user = serializer.save()
        user.is_email_verified = True
        user.save()
        
        send_verification_email.delay(user.id, user.email_verification_code)
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            {
                "id": serializer.data.get("id"),
                "email": serializer.data.get("email"),
                "message": "Пользователь успешно зарегистрирован. Проверьте электронную почту для подтверждения аккаунта."
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class EmailVerificationView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        verification_code = request.query_params.get('token')
        
        if not verification_code:
            return Response(
                {"error": "Не указан токен верификации"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(
                email_verification_code=verification_code,
                email_verification_expiration__gt=timezone.now()
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Недействительный или просроченный токен верификации"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_email_verified = True
        user.email_verification_code = None
        user.email_verification_expiration = None
        user.save()
        
        return Response(
            {"detail": "Email успешно подтвержден."},
            status=status.HTTP_200_OK
        )


class CharityListCreateView(generics.ListCreateAPIView):
    queryset = Charity.objects.all()
    serializer_class = CharitySerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CharityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Charity.objects.all()
    serializer_class = CharitySerializer
    permission_classes = [IsAuthenticated]


class NotificationListCreateView(generics.ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class CharityViewSet(viewsets.ModelViewSet):
    queryset = Charity.objects.all()
    serializer_class = CharitySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-sent_at')
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        notifications = self.get_queryset()
        notifications.update(is_read=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BalanceView(APIView):
    """
    Представление для получения информации о текущем балансе пользователя
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Получение текущего баланса пользователя",
        responses={
            200: openapi.Response(
                description="Успешный ответ с данными баланса",
                schema=BalanceSerializer
            ),
            404: "Баланс пользователя не найден"
        },
        tags=['balance']
    )
    def get(self, request):
        balance = get_object_or_404(Balance, user=request.user)
        serializer = BalanceSerializer(balance)
        return Response(serializer.data)


class TopUpBalanceView(APIView):
    """
    Представление для пополнения баланса пользователя
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Пополнение баланса пользователя",
        request_body=TopUpBalanceSerializer,
        responses={
            200: openapi.Response(
                description="Баланс успешно пополнен",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'balance': openapi.Schema(type=openapi.TYPE_NUMBER)
                    }
                )
            ),
            400: "Ошибка при пополнении баланса"
        },
        tags=['balance']
    )
    def post(self, request):
        serializer = TopUpBalanceSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            balance = get_object_or_404(Balance, user=request.user)
            
            try:
                new_balance = balance.top_up(amount)
                return Response({
                    "message": f"Баланс успешно пополнен на {amount} руб.",
                    "balance": new_balance
                }, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCharityView(APIView):
    """
    Представление для получения информации о благотворительной организации текущего пользователя
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Получение информации о благотворительной организации текущего пользователя",
        responses={
            200: CharitySerializer,
            404: "Благотворительная организация не найдена"
        },
        tags=['users']
    )
    def get(self, request):
        try:
            if request.user.role != 'charity':
                return Response(
                    {"detail": "Пользователь не является благотворительной организацией"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                charity = Charity.objects.get(user=request.user)
                serializer = CharitySerializer(charity)
                return Response(serializer.data)
            except Charity.DoesNotExist:
                return Response(
                    {"detail": "Не удалось определить благотворительную организацию. Убедитесь, что у вас есть права на создание аукциона."},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {"detail": f"Ошибка: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class SubscriptionView(APIView):
    """
    Представление для управления подпиской пользователя
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Получение информации о подписке пользователя",
        responses={
            200: openapi.Response(
                description="Информация о подписке",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'has_subscription': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'end_date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', nullable=True),
                        'auto_renewal': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            )
        },
        tags=['subscription']
    )
    def get(self, request):
        """Получение информации о подписке пользователя"""
        try:
            subscription = Subscription.objects.filter(user=request.user).first()
            
            if subscription:
                has_subscription = subscription.is_active and subscription.end_date > timezone.now()
                
                return Response({
                    'has_subscription': has_subscription,
                    'end_date': subscription.end_date if has_subscription else None,
                    'auto_renewal': subscription.auto_renewal if has_subscription else False
                })
            else:
                return Response({
                    'has_subscription': False,
                    'end_date': None,
                    'auto_renewal': False
                })
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Оформление подписки",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['payment_method'],
            properties={
                'payment_method': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['balance', 'card'],
                    description='Способ оплаты: balance - с баланса аккаунта, card - банковской картой'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Подписка успешно оформлена",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'has_subscription': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'end_date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Ошибка при оформлении подписки"
        },
        tags=['subscription']
    )
    def post(self, request):
        """Оформление новой подписки"""
        payment_method = request.data.get('payment_method')

        subscription_price = 500
        
        try:
            existing_subscription = Subscription.objects.filter(
                user=request.user, 
                is_active=True,
                end_date__gt=timezone.now()
            ).first()
            
            if existing_subscription:
                existing_subscription.end_date = existing_subscription.end_date + timedelta(days=30)
                existing_subscription.save()
                
                return Response({
                    'has_subscription': True,
                    'end_date': existing_subscription.end_date,
                    'message': 'Подписка успешно продлена'
                })

            if payment_method == 'balance':

                try:
                    balance = Balance.objects.get(user=request.user)
                    if balance.amount < subscription_price:
                        return Response(
                            {'detail': 'Недостаточно средств на балансе'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    balance.withdraw(subscription_price)
                except Balance.DoesNotExist:
                    return Response(
                        {'detail': 'Баланс пользователя не найден'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            elif payment_method == 'card':

                pass
            else:
                return Response(
                    {'detail': 'Неверный способ оплаты'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            end_date = timezone.now() + timedelta(days=30)
            subscription = Subscription.objects.create(
                user=request.user,
                is_active=True,
                end_date=end_date,
                auto_renewal=True
            )
            
            return Response({
                'has_subscription': True,
                'end_date': subscription.end_date,
                'message': 'Подписка успешно оформлена'
            })
            
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Отмена автопродления подписки",
        responses={
            200: openapi.Response(
                description="Автопродление отменено",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'end_date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time')
                    }
                )
            ),
            404: "Подписка не найдена"
        },
        tags=['subscription']
    )
    def delete(self, request):
        """Отмена автопродления подписки"""
        try:
            subscription = Subscription.objects.filter(
                user=request.user, 
                is_active=True
            ).first()
            
            if not subscription:
                return Response(
                    {'detail': 'У вас нет активной подписки'},
                    status=status.HTTP_404_NOT_FOUND
                )

            subscription.auto_renewal = False
            subscription.save()
            
            return Response({
                'message': 'Автопродление подписки отменено',
                'end_date': subscription.end_date
            })
            
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)