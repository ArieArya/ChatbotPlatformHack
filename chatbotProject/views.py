from django.shortcuts import render
from .models import UserDatabase, ChatbotAnalytics, ChatbotDatabase
from django.http import JsonResponse, HttpResponseBadRequest
import pandas as pd
import math
import json
import os
from datetime import datetime, timedelta
from random import randrange
from create_new_model import create_new_model
from chat_response import chat_response
from paraphrase_preprocess import preprocess_train_data
from get_template import get_template_json
import uuid


# login check
def login(request, username, password):
    response = {'user_exists': True, 'secret_key': ''}
    
    user_data = UserDatabase.objects.filter(username=username, password=password).values()
    
    if len(user_data) == 0:
        response['user_exists'] = False
    else:
        response['secret_key'] = user_data[0]['secretKey']
    
    return JsonResponse(response, safe=False)
    
    
# add new user
def create_new_user(request, username, password):
    response = {'request_success': True}
    
    # check if user already exists
    user_data = UserDatabase.objects.filter(
        username=username, password=password).values()
    
    if len(user_data) != 0:
        response['request_success'] = False
    
    else:
        # generate secret number for user
        secret_number = uuid.uuid1()
        
        # insert new user to database
        insertedDatabase = UserDatabase(username=username, password=password, secretKey=secret_number)
        
        # save database
        insertedDatabase.save()
        
    return JsonResponse(response, safe=False)


# train new model
def train_new_model(request, secret_key, model_name):
    
    # check if secret key exists
    user_data = UserDatabase.objects.filter(secretKey=secret_key).values()
    
    if len(user_data) == 0:
        return HttpResponseBadRequest('secret key does not exist')
        
    else:
        if request.method == 'POST':
            json_data = json.loads(request.body)
            # train_data = preprocess_train_data(json_data)
            
            create_new_model(secret_key, model_name, json_data)
            
            # check if model with same name already exists
            chatbot_data = ChatbotDatabase.objects.filter(secretKey=secret_key, botName=model_name).values()
            
            if len(chatbot_data) == 0:
                # insert new bot to database if not already in database
                chatbotDatabase = ChatbotDatabase(secretKey=secret_key, botName=model_name)
                
                # save database
                chatbotDatabase.save()
            
        else:
            return HttpResponseBadRequest('request is not POST')
    
    response = {'request_info': 'model trained successfully'}
    return JsonResponse(response, safe=False)


# delete trained model
def delete_model(request, secret_key, model_name):
    # check if model exists
    chatbot_data = ChatbotDatabase.objects.filter(secretKey=secret_key, botName=model_name).values()
    
    if len(chatbot_data) == 0:
        response = {'request_info': 'model not found'}
        return JsonResponse(response, safe=False)
    
    else:
        # delete model from database
        curChatbotDatabase = ChatbotDatabase.objects.filter(secretKey=secret_key, botName=model_name).delete()
    
        response = {'request_info': 'model deleted successfully'}
        return JsonResponse(response, safe=False)


# obtain new response
def get_response(request, secret_key, model_name, inp_message):
    # check if secret key exists
    user_data = UserDatabase.objects.filter(secretKey=secret_key).values()
    
    # check if model exists
    chatbot_data = ChatbotDatabase.objects.filter(secretKey=secret_key, botName=model_name).values()
    
    if len(user_data) == 0:
        return HttpResponseBadRequest('secret key does not exist')
    
    elif len(chatbot_data) == 0:
        return HttpResponseBadRequest('model ' + str(model_name) + ' does not exist')
    
    else:
        chat_result, tag_result = chat_response(secret_key, model_name, inp_message)
        response = {'chat_response': chat_result}
        
        # store in analytics database
        cur_date = datetime.utcnow()
        analyticsDatabase = ChatbotAnalytics(secretKey=secret_key, botName=model_name, date=cur_date, tag=tag_result, question=inp_message, response=chat_result)
        analyticsDatabase.save()
        
        return JsonResponse(response, safe=False)


# gets past queries and information
def get_past_data(request, secret_key, model_name, past_days):
    filter_date = datetime.utcnow() - timedelta(days=past_days)
    data_list = ChatbotAnalytics.objects.filter(date__gte=filter_date, secretKey=secret_key, botName=model_name).values()
    
    result_list = []
    for row in data_list:
        date = row['date']
        question = row['question']
        tag = row['tag']
        response = row['response']
        
        result_list.append({'date': date, 'question': question, 'tag': tag, 'response': response})
    
    return JsonResponse(result_list, safe=False)


# gets the most popular tags in the past n days
def get_popular_tags(request, secret_key, model_name, past_days):
    filter_date = datetime.utcnow() - timedelta(days=past_days)
    data_list = ChatbotAnalytics.objects.filter(date__gte=filter_date, secretKey=secret_key, botName=model_name).values()
    
    tag_counter = {}
    for row in data_list:
        tag = row['tag']
        
        if tag in tag_counter:
            tag_counter[tag] += 1
        else:
            tag_counter[tag] = 1
    
    result_list = []
    for tag_key, count in tag_counter.items():
        result_list.append({'tag':tag_key, 'count': count})
        
    result_list.sort(key = lambda x: x['count'], reverse=True)

    return JsonResponse(result_list, safe=False)


# gets the default json template
def get_template(request, template_name):
    json_template = get_template_json(template_name)
    return JsonResponse(json_template, safe=False)
