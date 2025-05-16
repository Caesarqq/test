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
    """
    Кастомный сериализатор для JWT токенов, проверяющий is_email_verified
    """
    def validate(self, attrs):
        # Получаем учетные данные из базового сериализатора
        data = super().validate(attrs)
        
        # Проверяем, подтвердил ли пользователь email
        if not self.user.is_email_verified:
            raise AuthenticationFailed('Аккаунт не подтвержден. Пожалуйста, проверьте вашу почту и подтвердите регистрацию.')
        
        # Добавляем дополнительные данные в ответ
        data['user_id'] = self.user.id
        data['email'] = self.user.email
        data['role'] = self.user.role
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Кастомное представление для получения JWT токена с проверкой подтверждения email
    """
    serializer_class = CustomTokenObtainPairSerializer


class ProfileView(generics.RetrieveAPIView):
    """
    Представление для получения информации о личном кабинете текущего пользователя
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Добавляем дополнительные данные, если необходимо
        # Например, количество уведомлений или другие агрегированные данные
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
    """
    Представление для регистрации нового пользователя с отправкой email
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        user = serializer.save()
        # Вызываем Celery задачу для отправки email
        send_verification_email.delay(user.id, user.email_verification_code)
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # Возвращаем успешный ответ с инструкцией проверить почту
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
    """
    Представление для подтверждения email по токену верификации
    через query параметр: /api/users/verify-email/?token=...
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Получаем токен из query параметра
        verification_code = request.query_params.get('token')
        
        if not verification_code:
            return Response(
                {"error": "Не указан токен верификации"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Ищем пользователя с таким кодом
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
        
        # Подтверждаем почту
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
            # Проверяем, что пользователь имеет роль 'charity'
            if request.user.role != 'charity':
                return Response(
                    {"detail": "Пользователь не является благотворительной организацией"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Находим связанную организацию
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
