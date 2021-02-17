from django.shortcuts import render
from .models import CryptoDatabase
from django.http import JsonResponse
import pandas as pd
import math
import json
import os
from datetime import datetime, timedelta


# Obtains all coins and their total count in past "past_hours" hours
def getAllCount(request, past_hours):  
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
    json_list = []
    for row in crypto_list:
        json_list.append({"symbol": row[0], "count": row[1]})

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


# Obtains hourly count of the top "n" coins in the past "past_hours" hours
def getNCountHourly(request, n, past_hours):
    filter_date = datetime.utcnow() - timedelta(hours=past_hours)
    data_list = CryptoDatabase.objects.filter(date__gte=filter_date).values()
    
    # collect data into dictionary
    crypto_dict = {}
    for row in data_list:
        crypto_symbol = row["symbol"]
        if crypto_symbol in crypto_dict:
            crypto_dict[crypto_symbol].append(
                {"date": row["date"], "count": row["count"]})
        else:
            crypto_dict[crypto_symbol] = [{"date": row["date"], "count": row["count"]}]
    
    # form new list to sort
    crypto_list = []
    for symbol, data in crypto_dict.items():
        crypto_list.append([symbol, data])
    crypto_list.sort(key=lambda x: sum([y["count"] for y in x[1]]), reverse=True)
    
    # form JSON list
    if n >= len(crypto_list):
        n = len(crypto_list)
    
    json_list = []
    for i in range(n):
        cur_symbol = crypto_list[i][0]
        cur_info = crypto_list[i][1]
        cur_info.sort(key=lambda x: x["date"], reverse=True) # sort by date
        
        json_list.append(
            {"symbol": cur_symbol, "crypto_info": cur_info})

    return JsonResponse(json_list, safe=False)


# Obtains total count of coin "crypto_symbol" in the past "past_hours" hours
def getCoinCountTotal(request, crypto_symbol, past_hours):
    filter_date = datetime.utcnow() - timedelta(hours=past_hours)
    data_list = CryptoDatabase.objects.filter(date__gte=filter_date, symbol=crypto_symbol).values()
    
    count = 0
    for row in data_list:
        count += row["count"]
    
    json_list = {"symbol": crypto_symbol, "count: ": count}
    return JsonResponse(json_list, safe=False)


# Obtains hourly count of coin "crypto_symbol" in the past "past_hours" hours
def getCoinCountHourly(request, crypto_symbol, past_hours):
    filter_date = datetime.utcnow() - timedelta(hours=past_hours)
    data_list = CryptoDatabase.objects.filter(date__gte=filter_date, symbol=crypto_symbol).values()

    # collect data into dictionary
    hourly_list = []
    for row in data_list:
        hourly_list.append({"date": row["date"], "count": row["count"]})
    hourly_list.sort(key=lambda x: x["date"], reverse=True)

    json_list = [{"symbol": crypto_symbol, "crypto_info": hourly_list}]

    return JsonResponse(json_list, safe=False)


# Obtains all hourly data of top "n" coin in the past "past_hours" hours
def getAllTopData(request, n, past_hours):
    filter_date = datetime.utcnow() - timedelta(hours=past_hours)
    data_list = CryptoDatabase.objects.filter(date__gte=filter_date).values()

    # collect data into dictionary
    crypto_dict = {}
    for row in data_list:
        crypto_symbol = row["symbol"]
        if crypto_symbol in crypto_dict:
            crypto_dict[crypto_symbol].append(
                {"date": row["date"], "count": row["count"], "popular_link": row["popular_link"], "price": row["price"], "marketcap": row["marketcap"], 
                 "volume_24h": row["volume_24h"], "percent_change_24h": row["percent_change_24h"], "percent_change_1h": row["percent_change_1h"]})
        else:
            crypto_dict[crypto_symbol] = [
                {"date": row["date"], "count": row["count"], "popular_link": row["popular_link"], "price": row["price"], "marketcap": row["marketcap"],
                 "volume_24h": row["volume_24h"], "percent_change_24h": row["percent_change_24h"], "percent_change_1h": row["percent_change_1h"]}]

    # form new list to sort
    crypto_list = []
    for symbol, data in crypto_dict.items():
        crypto_list.append([symbol, data])
    crypto_list.sort(key=lambda x: sum(
        [y["count"] for y in x[1]]), reverse=True)

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
        hourly_list.append({"date": row["date"], "count": row["count"], "popular_link": row["popular_link"], "price": row["price"], "marketcap": row["marketcap"],
                            "volume_24h": row["volume_24h"], "percent_change_24h": row["percent_change_24h"], "percent_change_1h": row["percent_change_1h"]})
    hourly_list.sort(key=lambda x: x["date"], reverse=True)
    
    json_list = [{"symbol": crypto_symbol, "crypto_info": hourly_list}]

    return JsonResponse(json_list, safe=False)


# e.g. combined_hours=2 will give combined data every 6 hours
def getAllTopDataCombinedHours(request, n, past_hours, combined_hours):
    filter_date = datetime.utcnow() - timedelta(hours=past_hours)
    data_list = CryptoDatabase.objects.filter(date__gte=filter_date).values()

    # collect data into dictionary
    crypto_dict = {}
    for row in data_list:
        crypto_symbol = row["symbol"]
        if crypto_symbol in crypto_dict:
            crypto_dict[crypto_symbol].append(
                {"date": row["date"], "count": row["count"], "popular_link": row["popular_link"], "price": row["price"], "marketcap": row["marketcap"],
                 "volume_24h": row["volume_24h"], "percent_change_24h": row["percent_change_24h"], "percent_change_1h": row["percent_change_1h"]})
        else:
            crypto_dict[crypto_symbol] = [
                {"date": row["date"], "count": row["count"], "popular_link": row["popular_link"], "price": row["price"], "marketcap": row["marketcap"],
                 "volume_24h": row["volume_24h"], "percent_change_24h": row["percent_change_24h"], "percent_change_1h": row["percent_change_1h"]}]

    # form new list to sort
    crypto_list = []
    for symbol, data in crypto_dict.items():
        crypto_list.append([symbol, data])
    
    # sort by count
    crypto_list.sort(key=lambda x: sum([y["count"] for y in x[1]]), reverse=True)
        
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
        idx_counter = 0
        cur_popular_count = 0
        cur_popular_link = ''
        
        for k in range(len(cur_symbol_list)):
            # adds count together
            cur_iter_count += cur_symbol_list[k]["count"]
            if cur_symbol_list[k]["count"] >= cur_popular_count:
                cur_popular_count = cur_symbol_list[k]["count"]
                cur_popular_link = cur_symbol_list[k]["popular_link"]
            
            idx_counter += 1
            if idx_counter == combined_hours:
                cur_iter_dict["count"] = cur_iter_count
                cur_iter_dict["popular_link"] = cur_popular_link
                new_symbol_list.append(cur_iter_dict)
                if k + 1 >= len(cur_symbol_list):
                    break
                cur_iter_dict = cur_symbol_list[k+1]
                idx_counter = 0
                cur_iter_count = 0 
                popular_count = 0
                popular_link = ''
            
        json_list.append(
            {"symbol": crypto_list[i][0], "crypto_info": new_symbol_list})

    
    return JsonResponse(json_list, safe=False)


# e.g. combined_hours=2 will give combined data every 6 hours
def getAllDataCoinCombinedHours(request, crypto_symbol, past_hours, combined_hours):
    filter_date = datetime.utcnow() - timedelta(hours=past_hours)
    data_list = CryptoDatabase.objects.filter(
        date__gte=filter_date, symbol=crypto_symbol).values()

    # collect data into dictionary
    hourly_list = []
    for row in data_list:
        hourly_list.append({"date": row["date"], "count": row["count"], "popular_link": row["popular_link"], "price": row["price"], "marketcap": row["marketcap"],
                            "volume_24h": row["volume_24h"], "percent_change_24h": row["percent_change_24h"], "percent_change_1h": row["percent_change_1h"]})
    hourly_list.sort(key=lambda x: x["date"], reverse=True)
    
    # combine hours
    cur_symbol_list = hourly_list
    new_symbol_list = []

    cur_iter_dict = cur_symbol_list[0]
    cur_iter_count = 0
    idx_counter = 0

    for k in range(len(cur_symbol_list)):
        # adds count together
        cur_iter_count += cur_symbol_list[k]["count"]
        idx_counter += 1
        if idx_counter == combined_hours:
            cur_iter_dict["count"] = cur_iter_count
            new_symbol_list.append(cur_iter_dict)
            if k + 1 >= len(cur_symbol_list):
                break
            cur_iter_dict = cur_symbol_list[k+1]
            idx_counter = 0
            cur_iter_count = 0
    

    json_list = [{"symbol": crypto_symbol, "crypto_info": new_symbol_list}]

    return JsonResponse(json_list, safe=False)
