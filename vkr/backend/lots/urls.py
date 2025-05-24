from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
app_name = 'lots'

router = DefaultRouter()
router.register(r'', views.LotViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'delivery', views.DeliveryDetailViewSet)
router.register(r'lot-images', views.LotImageViewSet, basename='lot-images')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/update/', views.LotUpdateView.as_view(), name='lot-update'),
    path('<int:pk>/delete/', views.LotDeleteView.as_view(), name='lot-delete'),
    path('<int:pk>/status/', views.LotStatusUpdateView.as_view(), name='lot-status-update'),
    path('<int:pk>/approve/', views.LotApproveView.as_view(), name='lot-approve'),
    path('<int:pk>/reject/', views.LotRejectView.as_view(), name='lot-reject'),
]
