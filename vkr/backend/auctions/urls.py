from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    AuctionCreateView, AuctionListView, AuctionDetailView, 
    AuctionUpdateView, AuctionDeleteView, AuctionTicketViewSet
)

app_name = 'auctions'

urlpatterns = [
    path('create/', AuctionCreateView.as_view(), name='auction-create'),
    path('', AuctionListView.as_view(), name='auction-list'),
    path('<int:pk>/', AuctionDetailView.as_view(), name='auction-detail'),
    path('<int:pk>/update/', AuctionUpdateView.as_view(), name='auction-update'),
    path('<int:pk>/delete/', AuctionDeleteView.as_view(), name='auction-delete'),

    path('tickets/', AuctionTicketViewSet.as_view({'get': 'list'}), name='auction-tickets-list'),
    path('tickets/<int:pk>/', AuctionTicketViewSet.as_view({'get': 'retrieve'}), name='auction-ticket-detail'),
    path('tickets/purchase/', AuctionTicketViewSet.as_view({'post': 'purchase'}), name='auction-ticket-purchase'),
    path('tickets/check-access/', AuctionTicketViewSet.as_view({'get': 'check_access'}), name='auction-ticket-check'),
]