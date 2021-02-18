"""crypto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from cryptoProject import views as v

urlpatterns = [
    # For admin purposes
    path('admin/', admin.site.urls),
    
    # Obtains all coins and their total count in past "past_hours" hours
    path('query&topCount=all&pastHours=<int:past_hours>', v.getAllCount),
    
    # Obtains the top "n" coins and their total count in past "past_hours" hours
    path('query&topCount=<int:n>&pastHours=<int:past_hours>', v.getNCount),
    
    # Obtains hourly count of the top "n" coins in the past "past_hours" hours
    path('query&hourlyCount=<int:n>&pastHours=<int:past_hours>', v.getNCountHourly),
    
    # Obtains total count of coin "crypto_symbol" in the past "past_hours" hours
    path('query&coinTotalCount=<str:crypto_symbol>&pastHours=<int:past_hours>',
         v.getCoinCountTotal),
    
    # Obtains hourly count of coin "crypto_symbol" in the past "past_hours" hours
    path('query&coinHourlyCount=<str:crypto_symbol>&pastHours=<int:past_hours>',
         v.getCoinCountHourly),
    
    # Obtains all hourly data of top "n" coin in the past "past_hours" hours
    path('query&hourlyCount=<int:n>&pastHours=<int:past_hours>&getAllData',
         v.getAllTopData),
    
    # Obtains all hourly data of coin "crypto_symbol" in the past "past_hours" hours
    path('query&coinTotalCount=<str:crypto_symbol>&pastHours=<int:past_hours>&getAllData',
         v.getAllDataCoin),
    
    # Obtains combined data for "combinedHours" hours of top "n" coins in the past "past_hours" hours
    path('query&hourlyCount=<int:n>&pastHours=<int:past_hours>&combinedHours=<int:combined_hours>&getAllData',
         v.getAllTopDataCombinedHours),
    
    # Obtains combined data for "combinedHours" hours of coin "crypto_symbol" in the past "past_hours" hours
    path('query&coinHourlyCount=<str:crypto_symbol>&pastHours=<int:past_hours>&combinedHours=<int:combined_hours>&getAllData',
         v.getAllDataCoinCombinedHours),
    
    # Obtains hourly performance score of the top "n" coins in the past "past_hours" hours
    path('query&hourlyScore=<int:n>&pastHours=<int:past_hours>', v.getNScoreHourly),
    
    # Obtains hourly performance score of coin "crypto_symbol" in the past "past_hours" hours
    path('query&coinHourlyScore=<str:crypto_symbol>&pastHours=<int:past_hours>',
         v.getCoinScoreHourly)
    
]
