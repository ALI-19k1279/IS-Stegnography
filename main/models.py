from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Stegno(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    filename=models.TextField()
    key=models.TextField()
    shareLink=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.user
    