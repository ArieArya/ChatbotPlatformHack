from django.db import models

# Create your models here.
class CryptoDatabase(models.Model):
    crypto_id = models.AutoField(primary_key=True)
    symbol = models.CharField(max_length=10)
    slug = models.CharField(max_length=50)
    date = models.DateTimeField()
    source = models.CharField(max_length=20)
    count = models.IntegerField()
    popular_link = models.TextField()
    popular_content = models.TextField()
    price = models.DecimalField(max_digits=40, decimal_places=10)
    marketcap = models.DecimalField(max_digits=40, decimal_places=10)
    volume_24h = models.DecimalField(max_digits=40, decimal_places=10)
    percent_change_24h = models.DecimalField(max_digits=15, decimal_places=10)
    percent_change_1h = models.DecimalField(max_digits=15, decimal_places=10)
    
    def __str__(self):
        return self.name


    
