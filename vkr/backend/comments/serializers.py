from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    user_display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'lot', 'user', 'user_username', 'user_display_name', 'content', 'created_at']
        read_only_fields = ['created_at', 'user']

    def get_user_display_name(self, obj):
        user = obj.user
        if user.first_name and user.last_name:
            return f"{user.first_name} {user.last_name}".strip()
        if user.first_name:
            return user.first_name
        if user.username:
            return user.username
        return user.email
