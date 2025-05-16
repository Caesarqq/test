from rest_framework import permissions
from .models import User


class IsOrganization(permissions.BasePermission):
    """
    Разрешение только для пользователей с ролью Организация (Charity)
    """
    message = "Только пользователи с ролью 'Благотворительная организация' могут выполнять это действие."
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.CHARITY


class IsDonor(permissions.BasePermission):
    """
    Разрешение только для пользователей с ролью Донор
    """
    message = "Только пользователи с ролью 'Донор' могут выполнять это действие."
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.DONOR


class IsOwner(permissions.BasePermission):
    """
    Разрешение только для владельца объекта
    """
    message = "Вы не являетесь владельцем данного объекта."
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'donor'):
            return obj.donor == request.user
        elif hasattr(obj, 'charity'):
            # Для аукционов - проверяем, что пользователь связан с благотворительной организацией
            return request.user.is_authenticated and hasattr(request.user, 'charity') and obj.charity == request.user.charity
        return False


class IsAuctionOwner(permissions.BasePermission):
    """
    Разрешение только для владельца аукциона (Организация)
    """
    message = "Вы не являетесь владельцем данного аукциона."
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'auction'):
            # Для лотов - проверяем владельца аукциона
            return request.user.is_authenticated and hasattr(request.user, 'charity') and obj.auction.charity == request.user.charity
        elif hasattr(obj, 'charity'):
            # Для аукционов - проверяем владельца напрямую
            return request.user.is_authenticated and hasattr(request.user, 'charity') and obj.charity == request.user.charity
        return False
