from django.db import models
from lots.models import Lot
from users.models import User


class Comment(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.lot.title}"
