"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from users.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from auctions.views import AuctionViewSet, AuctionEventViewSet
from lots.views import (
    LotViewSet, CategoryViewSet, LotCategoryViewSet, 
    LotImageViewSet, DeliveryDetailViewSet
)
from bids.views import BidViewSet, TransactionViewSet
from comments.views import CommentViewSet

router = DefaultRouter()

router.register(r'auctions', AuctionViewSet)
router.register(r'auction-events', AuctionEventViewSet)

router.register(r'lots', LotViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'lot-categories', LotCategoryViewSet)
router.register(r'lot-images', LotImageViewSet)
router.register(r'delivery-details', DeliveryDetailViewSet)

router.register(r'bids', BidViewSet)
router.register(r'transactions', TransactionViewSet)

router.register(r'comments', CommentViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Charity Auction API",
        default_version='v1',
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('api/', include(router.urls)),
    path('api/users/', include('users.urls')),

    path('api/v1/auctions/', include('auctions.urls')),
    path('api/v1/lots/', include('lots.urls')),
    
    path('api-auth/', include('rest_framework.urls')),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)