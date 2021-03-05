from django.db import models

# Create your models here.
class ChatbotDatabase(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.TextField()
    password = models.TextField()
    secretKey = models.TextField()
    
    def __str__(self):
        return self.name


    
