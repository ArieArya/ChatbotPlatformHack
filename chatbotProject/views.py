from django.shortcuts import render
from .models import ChatbotDatabase, ChatbotAnalytics
from django.http import JsonResponse
import pandas as pd
import math
import json
import os
from datetime import datetime, timedelta
from random import randrange
from create_new_model import create_new_model
from chat_response import chat_response


# temporary
def temp(request):
    json_list = []
    return JsonResponse(json_list, safe=False)


# login check
def login(request, username, password):
    response = {'user_exists': True, 'secret_key': ''}
    
    user_data = ChatbotDatabase.objects.filter(username=username, password=password).values()
    print("user_data: ", user_data)
    
    if len(user_data) == 0:
        response['user_exists'] = False
    else:
        response['secret_key'] = user_data[0]['secretKey']
    
    return JsonResponse(response, safe=False)
    
    
# add new user
def create_new_user(request, username, password):
    response = {'request_info': 'user created successfully'}
    
    # check if user already exists
    user_data = ChatbotDatabase.objects.filter(
        username=username, password=password).values()
    
    if len(user_data) != 0:
        response['request_info'] = 'username already exists'
    
    else:
        # generate secret number for user
        secret_number = randrange(1000000)
        
        # insert new user to database
        insertedDatabase = ChatbotDatabase(username=username, password=password, secretKey=secret_number)
        
        # save database
        insertedDatabase.save()
        
    return JsonResponse(response, safe=False)


# train new model
def train_new_model(request, secret_key):
    response = {'request_info': 'model trained successfully'}
    
    # check if secret key exists
    user_data = ChatbotDatabase.objects.filter(secretKey=secret_key).values()
    
    if len(user_data) == 0:
        response['request_info'] = 'user does not exist'
        
    else:
        if request.method == 'POST':
            json_data = json.loads(request.body)
            
            create_new_model(secret_key, json_data)
            
        else:
            response['request_info'] = 'json data not parsed correctly'
    
    return JsonResponse(response, safe=False)


# obtain new response
def get_response(request, secret_key, inp_message):
    # check if secret key exists
    user_data = ChatbotDatabase.objects.filter(secretKey=secret_key).values()
    if len(user_data) == 0:
        response = {'chat_response': ''}
    
    else:
        chat_result, tag_result = chat_response(secret_key, inp_message)
        response = {'chat_response': chat_result}
        
        # store in analytics database
        cur_date = datetime.utcnow()
        analyticsDatabase = ChatbotAnalytics(secretKey=secret_key, date=cur_date, tag=tag_result, question=inp_message, response=chat_result)
        analyticsDatabase.save()
        
    return JsonResponse(response, safe=False)


# gets past queries and information
def get_past_data(request, secret_key, past_days):
    filter_date = datetime.utcnow() - timedelta(days=past_days)
    data_list = ChatbotAnalytics.objects.filter(date__gte=filter_date, secretKey=secret_key).values()
    
    result_list = []
    for row in data_list:
        date = row['date']
        question = row['question']
        tag = row['tag']
        response = row['response']
        
        result_list.append({'date': date, 'question': question, 'tag': tag, 'response': response})
    
    return JsonResponse(result_list, safe=False)

