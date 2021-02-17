from django.db import models

# Create your models here.
class CryptoDatabase(models.Model):
    crypto_id = models.AutoField(primary_key=True)
    symbol = models.CharField(max_length=10)
    date = models.DateTimeField()
    source = models.CharField(max_length=20)
    count = models.IntegerField()
    popular_link = models.CharField(max_length=300)
    price = models.DecimalField(max_digits=15, decimal_places=10)
    marketcap = models.DecimalField(max_digits=25, decimal_places=10)
    volume_24h = models.DecimalField(max_digits=25, decimal_places=10)
    percent_change_24h = models.DecimalField(max_digits=15, decimal_places=10)
    percent_change_1h = models.DecimalField(max_digits=15, decimal_places=10)
    
    def __str__(self):
        return self.name


    
