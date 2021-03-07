from django.db import models

# Create your models here.
class UserDatabase(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.TextField()
    password = models.TextField()
    secretKey = models.TextField()
    
    def __str__(self):
        return self.name

class ChatbotDatabase(models.Model):
    secretKey = models.TextField()
    botName = models.TextField()
    
    def __str__(self):
        return self.name

class ChatbotAnalytics(models.Model):
    secretKey = models.TextField()
    botName = models.TextField()
    date = models.DateTimeField()
    tag = models.TextField()
    question = models.TextField()
    response = models.TextField()
    
    def __str__(self):
        return self.name
