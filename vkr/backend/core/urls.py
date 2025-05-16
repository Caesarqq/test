from django.urls import path, include

urlpatterns = [
    path('api/users/', include('users.urls')),
    path('api/auctions/', include('auctions.urls')),
    path('api/lots/', include('lots.urls', namespace='lots')),
    path('api/bids/', include('bids.urls')),
    path('api/comments/', include('comments.urls')),
]
