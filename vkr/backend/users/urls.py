from django.urls import path
from users.models import Subscription
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
    UserCharityView,
    SubscriptionView
)

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),

    path('profile/', ProfileView.as_view(), name='profile'),

    path('me/charity/', UserCharityView.as_view(), name='user-charity'),

    path('users/', UserListView.as_view(), name='user-list'),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/<str:pk>/', UserDetailView.as_view(), name='user-detail'),

    path('charities/', CharityListCreateView.as_view(), name='charity-list'),
    path('charities/<int:pk>/', CharityDetailView.as_view(), name='charity-detail'),

    path('notifications/', NotificationListCreateView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),

    path('balance/', BalanceView.as_view(), name='balance'),
    path('balance/top-up/', TopUpBalanceView.as_view(), name='balance-top-up'),

    path('subscription/', SubscriptionView.as_view(), name='subscription'),
]
