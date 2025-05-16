from django.shortcuts import render
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from lots.models import Lot

from .models import Comment
from .serializers import CommentSerializer
from .permissions import IsAuthorOrReadOnly


class CommentViewSet(viewsets.ModelViewSet):
    """
    CRUD для комментариев к лотам.
    - List/Read: публично
    - Create: только авторизованный пользователь (JWT)
    - Update/Delete: только автор комментария
    Фильтрация по lot (lot_id).
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['lot']
    # Пагинация берётся из глобальных настроек DRF

    def perform_create(self, serializer):
        lot = serializer.validated_data['lot']
        if lot.status != 'approved':
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Можно комментировать только одобренные лоты.')
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Создать новый комментарий. Требуется JWT-токен.",
        request_body=CommentSerializer,
        responses={201: CommentSerializer},
        security=[{'Bearer': []}]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Обновить комментарий. Только автор. Требуется JWT-токен.",
        request_body=CommentSerializer,
        responses={200: CommentSerializer},
        security=[{'Bearer': []}]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Частично обновить комментарий. Только автор. Требуется JWT-токен.",
        request_body=CommentSerializer,
        responses={200: CommentSerializer},
        security=[{'Bearer': []}]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
