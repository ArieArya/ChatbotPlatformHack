from django.shortcuts import render
from .models import CryptoDatabase
from django.http import JsonResponse
import pandas as pd
import math
import json
import os
from datetime import datetime, timedelta

# Tanh function
def hyp_tan(val):
    return 10*math.tanh(val/1000)

# Get all Crypto Symbol Names
def getSymbols(request):
    filter_date = datetime.utcnow() - timedelta(hours=3)
    data_list = CryptoDatabase.objects.filter(date__gte=filter_date).values()
    
    # collect count to a dictionary
    crypto_dict = {}
    for row in data_list:
        crypto_symbol = row["symbol"]
        count = row["count"]
        marketcap = row["marketcap"]
        percentchange = row["percent_change_24h"]
        volume = row["volume_24h"]


        if crypto_symbol not in crypto_dict:
            crypto_dict[crypto_symbol] = {
                "slug": "TEMP_SLUG", "price": row["price"], "marketcap": row["marketcap"], "volume_24h": row["volume_24h"],
                "percent_change_24h": row["percent_change_24h"], "percent_change_1h": row["percent_change_1h"]}
    
    # form new list 
    crypto_list = []
    for symbol, data in crypto_dict.items():
        crypto_list.append([symbol, data])

    json_list = []
    for i in range(len(crypto_list)):
        cur_symbol = crypto_list[i][0]
        cur_info = crypto_list[i][1]
        print("type: ", type(cur_info))

        json_list.append(
            {"symbol": cur_symbol, "slug": cur_info["slug"], "price": cur_info["price"], "marketcap": cur_info["marketcap"], "volume_24h": cur_info["volume_24h"],
             "percent_change_24h": cur_info["percent_change_24h"], "percent_change_1h": cur_info["percent_change_1h"]})

    return JsonResponse(json_list, safe=False)
    

# Obtains the top "n" coins and their total count in past "past_hours" hours
def getNCount(request, n, past_hours):
    filter_date = datetime.utcnow() - timedelta(hours=past_hours)
    data_list = CryptoDatabase.objects.filter(date__gte=filter_date).values()

    # collect count to a dictionary
    crypto_dict = {}
    for row in data_list:
        if row["symbol"] in crypto_dict:
            crypto_dict[row["symbol"]] += row["count"]
        else:
            crypto_dict[row["symbol"]] = row["count"]

    # form new list to sort
    crypto_list = []
    for symbol, count in crypto_dict.items():
        crypto_list.append([symbol, count])
    crypto_list.sort(key=lambda x: x[1], reverse=True)

    # form JSON list
    if n >= len(crypto_list):
        n = len(crypto_list)
        
    json_list = []
    for i in range(n):
        json_list.append({"symbol": crypto_list[i][0], "count": crypto_list[i][1]})

    return JsonResponse(json_list, safe=False)


# Obtains the top "n" coins and their total score in past "past_hours" hours
def getNScore(request, n, past_hours):
    filter_date = datetime.utcnow() - timedelta(hours=past_hours)
    data_list = CryptoDatabase.objects.filter(date__gte=filter_date).values()

    # collect count to a dictionary
    crypto_dict = {}
    for row in data_list:
        crypto_symbol = row["symbol"]
        count = row["count"]
        marketcap = row["marketcap"]
        percentchange = row["percent_change_24h"]
        volume = row["volume_24h"]

        try:
            # calculate performance
            performance_score = hyp_tan(count * (volume / marketcap) * (1 + (percentchange/100)))
            if crypto_symbol in crypto_dict:
                crypto_dict[crypto_symbol] += performance_score
            else:
                crypto_dict[crypto_symbol] = performance_score

        except:
            print("Zero marketcap for coin: ", crypto_symbol)

    # form new list to sort
    crypto_list = []
    for symbol, score in crypto_dict.items():
        crypto_list.append([symbol, score])
    crypto_list.sort(key=lambda x: x[1], reverse=True)

    # form JSON list
    if n >= len(crypto_list):
        n = len(crypto_list)

    json_list = []
    for i in range(n):
        json_list.append(
            {"symbol": crypto_list[i][0], "score": crypto_list[i][1]})

    return JsonResponse(json_list, safe=False)


# Obtains total count of coin "crypto_symbol" in the past "past_hours" hours
def getCoinCountScoreTotal(request, crypto_symbol, past_hours):
    filter_date = datetime.utcnow() - timedelta(hours=past_hours)
    data_list = CryptoDatabase.objects.filter(date__gte=filter_date, symbol=crypto_symbol).values()
    
    acc_count = 0
    acc_score = 0
    for row in data_list:
        count = row["count"]
        marketcap = row["marketcap"]
        percentchange = row["percent_change_24h"]
        volume = row["volume_24h"]
        
        acc_count += count
        
        try:
            # calculate performance
            performance_score = hyp_tan(count * (volume / marketcap) * (1 + (percentchange/100)))
            acc_score += performance_score
            
        except:
            print("Zero marketcap for coin: ", crypto_symbol)
    
    json_list = {"symbol": crypto_symbol, "crypto_info: ": {"count": acc_count, "score": acc_score}}
    return JsonResponse(json_list, safe=False)



# Obtains all hourly data of top "n" coins by performance score in the past "past_hours" hours
def getAllTopData(request, n, past_hours):
    filter_date = datetime.utcnow() - timedelta(hours=past_hours)
    data_list = CryptoDatabase.objects.filter(date__gte=filter_date).values()

    # collect data into dictionary
    crypto_dict = {}
    for row in data_list:
        crypto_symbol = row["symbol"]
        count = row["count"]
        marketcap = row["marketcap"]
        percentchange = row["percent_change_24h"]
        volume = row["volume_24h"]

        try:
            # calculate performance
            performance_score = hyp_tan(count * (volume / marketcap) * (1 + (percentchange/100)))
        
            if crypto_symbol in crypto_dict:
                crypto_dict[crypto_symbol].append(
                    {"date": row["date"], "slug": "TEMP_SLUG", "count": row["count"], "score": performance_score, "popular_link": row["popular_link"], "price": row["price"], "marketcap": row["marketcap"],
                    "volume_24h": row["volume_24h"], "percent_change_24h": row["percent_change_24h"], "percent_change_1h": row["percent_change_1h"]})
            else:
                crypto_dict[crypto_symbol] = [
                    {"date": row["date"], "slug": "TEMP_SLUG", "count": row["count"], "score": performance_score, "popular_link": row["popular_link"], "price": row["price"], "marketcap": row["marketcap"],
                    "volume_24h": row["volume_24h"], "percent_change_24h": row["percent_change_24h"], "percent_change_1h": row["percent_change_1h"]}]
        except:
            print("Zero marketcap for coin: ", crypto_symbol)
            

    # form new list to sort
    crypto_list = []
    for symbol, data in crypto_dict.items():
        crypto_list.append([symbol, data])
    crypto_list.sort(key=lambda x: sum(
        [y["score"] for y in x[1]]), reverse=True)

    # form JSON list
    if n >= len(crypto_list):
        n = len(crypto_list)

    json_list = []
    for i in range(n):
        cur_symbol = crypto_list[i][0]
        cur_info = crypto_list[i][1]
        cur_info.sort(key=lambda x: x["date"], reverse=True)  # sort by date
        
        json_list.append(
            {"symbol": cur_symbol, "crypto_info": cur_info})

    return JsonResponse(json_list, safe=False)
    

# Obtains all hourly data of coin "crypto_symbol" in the past "hours" hours
def getAllDataCoin(request, crypto_symbol, past_hours):
    filter_date = datetime.utcnow() - timedelta(hours=past_hours)
    data_list = CryptoDatabase.objects.filter(
        date__gte=filter_date, symbol=crypto_symbol).values()

    # collect data into dictionary
    hourly_list = []
    for row in data_list:
        count = row["count"]
        marketcap = row["marketcap"]
        percentchange = row["percent_change_24h"]
        volume = row["volume_24h"]
        
        try:
            # calculate performance
            performance_score = hyp_tan(count * (volume / marketcap) * (1 + (percentchange/100)))
            hourly_list.append({"date": row["date"], "slug": "TEMP_SLUG", "count": row["count"], "score": performance_score, "popular_link": row["popular_link"], "price": row["price"], "marketcap": row["marketcap"],
                                "volume_24h": row["volume_24h"], "percent_change_24h": row["percent_change_24h"], "percent_change_1h": row["percent_change_1h"]})
        
        except:
            print("Zero marketcap for coin: ", crypto_symbol)
            
    hourly_list.sort(key=lambda x: x["date"], reverse=True)
    
    json_list = [{"symbol": crypto_symbol, "crypto_info": hourly_list}]

    return JsonResponse(json_list, safe=False)


# Combines data over multiple hours together
def getAllTopDataCombinedHours(request, n, past_hours, combined_hours):
    filter_date = datetime.utcnow() - timedelta(hours=past_hours)
    data_list = CryptoDatabase.objects.filter(date__gte=filter_date).values()

    # collect data into dictionary
    crypto_dict = {}
    for row in data_list:
        crypto_symbol = row["symbol"]
        count = row["count"]
        marketcap = row["marketcap"]
        percentchange = row["percent_change_24h"]
        volume = row["volume_24h"]

        try:
            # calculate performance
            performance_score = hyp_tan(count * (volume / marketcap) * (1 + (percentchange/100)))

            if crypto_symbol in crypto_dict:
                crypto_dict[crypto_symbol].append(
                    {"date": row["date"], "slug": "TEMP_SLUG", "count": row["count"], "score": performance_score, "popular_link": row["popular_link"], "price": row["price"], "marketcap": row["marketcap"],
                     "volume_24h": row["volume_24h"], "percent_change_24h": row["percent_change_24h"], "percent_change_1h": row["percent_change_1h"]})
            else:
                crypto_dict[crypto_symbol] = [
                    {"date": row["date"], "slug": "TEMP_SLUG", "count": row["count"], "score": performance_score, "popular_link": row["popular_link"], "price": row["price"], "marketcap": row["marketcap"],
                     "volume_24h": row["volume_24h"], "percent_change_24h": row["percent_change_24h"], "percent_change_1h": row["percent_change_1h"]}]
        except:
            print("Zero marketcap for coin: ", crypto_symbol)

    # form new list to sort
    crypto_list = []
    for symbol, data in crypto_dict.items():
        crypto_list.append([symbol, data])
    
    # sort by score
    crypto_list.sort(key=lambda x: sum([y["score"] for y in x[1]]), reverse=True)
        
    # form JSON list
    if n >= len(crypto_list):
        n = len(crypto_list)
    
    # combine hours
    json_list = []
    for i in range(n):
        cur_symbol_list = crypto_list[i][1]
        cur_symbol_list.sort(key=lambda x: x["date"], reverse=True)  # list of dicts
        new_symbol_list = []
        
        cur_iter_dict = cur_symbol_list[0]
        cur_iter_count = 0
        cur_iter_score = 0
        
        idx_counter = 0
        cur_popular_count = 0
        cur_popular_link = ''
        
        for k in range(len(cur_symbol_list)):
            # adds count and score together
            cur_iter_count += cur_symbol_list[k]["count"]
            cur_iter_score += cur_symbol_list[k]["score"]
            idx_counter += 1
            
            if cur_symbol_list[k]["count"] >= cur_popular_count:
                cur_popular_count = cur_symbol_list[k]["count"]
                cur_popular_link = cur_symbol_list[k]["popular_link"]
            
            if idx_counter == combined_hours:
                cur_iter_dict["count"] = cur_iter_count
                cur_iter_dict["score"] = cur_iter_score
                cur_iter_dict["popular_link"] = cur_popular_link
                new_symbol_list.append(cur_iter_dict)
                
                if k + 1 >= len(cur_symbol_list):
                    break
                
                # reset all variables
                cur_iter_dict = cur_symbol_list[k+1]
                idx_counter = 0
                cur_iter_count = 0
                cur_iter_score = 0
                popular_count = 0
                popular_link = ''
            
        json_list.append(
            {"symbol": crypto_list[i][0], "crypto_info": new_symbol_list})

    
    return JsonResponse(json_list, safe=False)


# Combines data over multiple hours together
def getAllDataCoinCombinedHours(request, crypto_symbol, past_hours, combined_hours):
    filter_date = datetime.utcnow() - timedelta(hours=past_hours)
    data_list = CryptoDatabase.objects.filter(
        date__gte=filter_date, symbol=crypto_symbol).values()

    # collect data into dictionary
    hourly_list = []
    for row in data_list:
        count = row["count"]
        marketcap = row["marketcap"]
        percentchange = row["percent_change_24h"]
        volume = row["volume_24h"]

        try:
            # calculate performance
            performance_score = hyp_tan(count * (volume / marketcap) * (1 + (percentchange/100)))
            hourly_list.append({"date": row["date"], "slug": "TEMP_SLUG", "count": row["count"], "score": performance_score, "popular_link": row["popular_link"], "price": row["price"], "marketcap": row["marketcap"],
                                "volume_24h": row["volume_24h"], "percent_change_24h": row["percent_change_24h"], "percent_change_1h": row["percent_change_1h"]})

        except:
            print("Zero marketcap for coin: ", crypto_symbol)
            
    hourly_list.sort(key=lambda x: x["date"], reverse=True)
    
    # combine hours
    cur_symbol_list = hourly_list
    new_symbol_list = []

    cur_iter_dict = cur_symbol_list[0]
    cur_iter_count = 0
    cur_iter_score = 0
    
    idx_counter = 0
    cur_popular_count = 0
    cur_popular_link = ''

    for k in range(len(cur_symbol_list)):
        # adds count and score together
        cur_iter_count += cur_symbol_list[k]["count"]
        cur_iter_score += cur_symbol_list[k]["score"]
        idx_counter += 1
        
        if cur_symbol_list[k]["count"] >= cur_popular_count:
            cur_popular_count = cur_symbol_list[k]["count"]
            cur_popular_link = cur_symbol_list[k]["popular_link"]
        
        if idx_counter == combined_hours:
            cur_iter_dict["count"] = cur_iter_count
            cur_iter_dict["score"] = cur_iter_score
            cur_iter_dict["popular_link"] = cur_popular_link
            new_symbol_list.append(cur_iter_dict)
            
            if k + 1 >= len(cur_symbol_list):
                break
            
            # reset all variables
            cur_iter_dict = cur_symbol_list[k+1]
            idx_counter = 0
            cur_iter_count = 0
            cur_iter_score = 0
            popular_count = 0
            popular_link = ''
    

    json_list = [{"symbol": crypto_symbol, "crypto_info": new_symbol_list}]

    return JsonResponse(json_list, safe=False)


