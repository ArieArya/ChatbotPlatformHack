"""chatbot URL Configuration

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
from chatbotProject import views as v

urlpatterns = [
    # For admin purposes
    path('admin/', admin.site.urls),
    
    # Login
    path('login/username=<str:username>/password=<str:password>', v.login),
    
    # Create new User
    path('createUser/username=<str:username>/password=<str:password>', v.create_new_user),
    
    # Train new model
    path('trainNewModel/secretkey=<str:secret_key>', v.train_new_model),

    # Obtain response from model
    path('getResponse/secretkey=<str:secret_key>/message=<str:inp_message>', v.get_response),
    
    # Obtain past historical data
    path('getPastData/secretkey=<str:secret_key>/pastDays=<int:past_days>', v.get_past_data),
    
    # Obtain most popular tags
    path('getPopularTags/secretkey=<str:secret_key>/pastDays=<int:past_days>', v.get_popular_tags)
]
