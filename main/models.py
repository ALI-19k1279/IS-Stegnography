from django.db import models
from django.contrib.auth.models import User
import uuid
import os

    
class Steg(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE) 
    filename=models.CharField(max_length=50)
    user_key=models.CharField(max_length=100)
    generated_key=models.CharField(max_length=100)
    salt=models.CharField(max_length=150)
    nonce=models.CharField(max_length=150)
    tag=models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.filename
    
# class Folder(models.Model):
#     uid = models.UUIDField(primary_key= True , editable= False , default=uuid.uuid4)
#     created_at = models.DateField(auto_now= True)
 

def get_upload_path(instance , filename):
     return os.path.join(str(instance.folder.uid) , filename)


class UserFiles(models.Model):
    uid = models.UUIDField(primary_key= True , editable= False , default=uuid.uuid4)
    user=models.ForeignKey(User,on_delete=models.CASCADE) 
    file = models.FileField(upload_to=get_upload_path)
    created_at = models.DateField(auto_now= True)
    

# class videoFrames(models.Model):
#     user=models.ForeignKey(User,on_delete=models.CASCADE) 
#     frames=models.A