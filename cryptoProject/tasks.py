from __future__ import absolute_import
from .models import CryptoDatabase
import os
from celery import shared_task
import json
import requests
import praw
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
from datetime import datetime, timedelta

@shared_task()
def deleteOldData():
    # Deletes all rows more than two weeks ago
    two_weeks_ago = datetime.utcnow() - timedelta(days=14)
    curCryptoDatabase = CryptoDatabase.objects.filter(date__lt=two_weeks_ago).delete()
    curCryptoDatabase.save()
    

@shared_task()
def insertNewCryptoData():
    # Read secret file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/secrets.txt') as f:
        secret = f.readlines()
    secrets = [x.strip() for x in secret]

    client_id = secrets[0]
    client_secret = secrets[1]
    username = secrets[2]
    password = secrets[3]
    api_key_1 = secrets[4]
    api_key_2 = secrets[5]
    api_key_3 = secrets[6]
    api_key_4 = secrets[7]
    
    coinmarketcapAPI = [api_key_1,
                        api_key_2,
                        api_key_3,
                        api_key_4]
    
    # Connect to CoinMarketCapAPI
    coinmarketcap = CoinMarketCapAPI(coinmarketcapAPI[0])
    crypto_listings = coinmarketcap.cryptocurrency_map().data
    cur_date = datetime.utcnow()
    
    crypto_list = []
    crypto_dict = {}
    crypto_slug_dict = {}
    crypto_slug_names = {}
    crypto_link_count_dict = {}
    crypto_link_dict = {}
    
    
    # exclude certain crypto
    crypto_exclude_dict = {'A': 0, 'CAP': 0, 'TOP': 0, 'OK': 0, 'ANY': 0, 'CAN': 0, 'JST': 0}
    
    for crypto_name in crypto_listings:
        crypto_symbol = crypto_name["symbol"]
        crypto_slug = crypto_name["slug"]
        if crypto_symbol.isalnum() and not crypto_symbol in crypto_exclude_dict: 
            crypto_list.append(crypto_symbol)
            crypto_slug_dict[crypto_slug.lower()] = crypto_symbol
            crypto_slug_names[crypto_symbol] = crypto_slug
            crypto_dict[crypto_symbol] = 0
            crypto_link_count_dict[crypto_symbol] = 0
            crypto_link_dict[crypto_symbol] = ['', '']
            
    # Perform web scraping
    scrape_period = cur_date - timedelta(hours=6)

    # Connect to reddit API
    print("Scraping the web...")
    reddit = praw.Reddit(client_id='Vht-J5m9WtgOVQ',
                         client_secret=client_secret,
                         username=username,
                         password=password,
                         user_agent='crypto_scraper')

    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/subreddits.txt') as f:
        content = f.readlines()
    subreddit_list = [x.strip() for x in content]

    # Obtain the string of all relevant posts
    post_list = []
    for subreddit_name in subreddit_list:
        subreddit = reddit.subreddit(subreddit_name)
        hot_topics = subreddit.hot(limit=1000)

        for submissions in hot_topics:
            if datetime.utcfromtimestamp(submissions.created_utc) >= scrape_period:
                post_list.append([submissions.title, submissions.score, submissions.permalink])
    
    # Count mentions of each cryptos in posts
    for submission in post_list:
        topics = submission[0]
        upvotes = submission[1]
        url = 'https://www.reddit.com/' + str(submission[2])
        
        word_list = topics.split()
        for words in word_list:
            # strip words to alphanumeric (remove special characters)
            if not words.isalnum():  
                words = ''.join(c for c in words if c.isalnum()) 
                
            if words in crypto_dict:
                crypto_dict[words] += upvotes
                if upvotes >= crypto_link_count_dict[words]:
                    crypto_link_count_dict[words] = upvotes
                    crypto_link_dict[words] = [url, topics]
                
            elif words.lower() in crypto_slug_dict: 
                cor_symbol = crypto_slug_dict[words.lower()]
                crypto_dict[cor_symbol] += upvotes
                if upvotes >= crypto_link_count_dict[cor_symbol]:
                    crypto_link_count_dict[cor_symbol] = upvotes
                    crypto_link_dict[cor_symbol] = [url, topics]

    # Update the price and market cap for each crypto symbol
    print("Inserting Crypto Data...")
    i = 0
    api_counter = 0
    while i < len(crypto_list):
        if i + 1000 >= len(crypto_list):
            crypto_query_str = crypto_list[i:len(crypto_list)]
            i = len(crypto_list)

        else:
            crypto_query_str = crypto_list[i:i+1000]
            i += 1000

        coinmarketcap = CoinMarketCapAPI(coinmarketcapAPI[api_counter])
        crypto_quotes = coinmarketcap.cryptocurrency_quotes_latest(
            symbol=str(','.join(crypto_query_str))).data
        
        api_counter += 1
        if api_counter >= len(coinmarketcapAPI):
            api_counter = 0

        for crypto_symbol in crypto_query_str:
            try:
                cur_price = round(crypto_quotes[crypto_symbol]['quote']['USD']['price'], 9)
                cur_marketcap = round(crypto_quotes[crypto_symbol]['quote']['USD']['market_cap'], 9)
                cur_vol = round(crypto_quotes[crypto_symbol]['quote']['USD']['volume_24h'], 9)
                cur_percent_change_24h = round(
                    crypto_quotes[crypto_symbol]['quote']['USD']['percent_change_24h'], 5)
                cur_percent_change_1h = round(
                    crypto_quotes[crypto_symbol]['quote']['USD']['percent_change_1h'], 5)
                cur_count = crypto_dict[crypto_symbol]

                curCryptoDatabase = CryptoDatabase(symbol=crypto_symbol, slug=crypto_slug_names[crypto_symbol], date=cur_date, source='reddit', count=cur_count, popular_link=crypto_link_dict[crypto_symbol][0],
                                                    popular_content=crypto_link_dict[crypto_symbol][1], price=cur_price, marketcap=cur_marketcap, volume_24h=cur_vol, 
                                                    percent_change_24h=cur_percent_change_24h, percent_change_1h=cur_percent_change_1h)
                # Save database
                curCryptoDatabase.save()
            
            except:
                print("invalid coin: ", crypto_symbol)

    return
