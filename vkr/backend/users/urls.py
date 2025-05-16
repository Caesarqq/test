from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import (
    UserListView,
    UserDetailView,
    UserCreateView,
    CharityListCreateView,
    CharityDetailView,
    NotificationListCreateView,
    NotificationDetailView,
    RegisterView,
    EmailVerificationView,
    CustomTokenObtainPairView,
    ProfileView,
    BalanceView,
    TopUpBalanceView,
    UserCharityView
)

urlpatterns = [
    # Аутентификация с использованием JWT
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Регистрация и верификация email
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    
    # Личный кабинет пользователя
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Получение информации о благотворительной организации текущего пользователя
    path('me/charity/', UserCharityView.as_view(), name='user-charity'),
    
    # Пользователи
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/<str:pk>/', UserDetailView.as_view(), name='user-detail'),
    
    # Благотворительные организации
    path('charities/', CharityListCreateView.as_view(), name='charity-list'),
    path('charities/<int:pk>/', CharityDetailView.as_view(), name='charity-detail'),
    
    # Уведомления
    path('notifications/', NotificationListCreateView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    
    # Баланс
    path('balance/', BalanceView.as_view(), name='balance'),
    path('balance/top-up/', TopUpBalanceView.as_view(), name='balance-top-up'),
]
