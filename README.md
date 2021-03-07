# API Documentation
Please find the main API url in <a href='http://ec2-18-135-99-244.eu-west-2.compute.amazonaws.com/'>this link.</a>

## Login
Each user will have their corresponding username, password, and secret key stored in the back-end database. Upon logging into the system, a secret key will be returned
to the front-end user. The login API is shown below:
```
/login/username=<str:username>/password=<str:password>
```
The response has the following format:
```python
{'user_exists': <bool>, 'secret_key': <str>}
```
'user_exists' returns a bool of whether or not the username and password matches any entries in the database, whilst 'secret_key' is the returned user secret key.


## Create New User
To create a new user, the following API call must be made:
```
/createUser/username=<str:username>/password=<str:password>
```
The response has the following format:
```python
{'request_success': <bool>}
```
'request_success' returns a bool of whether or not the new user has successfully been created. The only fail criteria is if the username already exists in the database.

## Train new chatbot model / Update existing chatbot model
To train a new chatbot model / update an existing chatbot model, a POST request must be made to the following url:
```
/trainNewModel/secretkey=<str:secret_key>/modelName=<str:model_name>
```
If the passed secret key is invalid or if the chatbot name already exists, a HTTP 400 Bad Request will be raised. The POST request must contain a JSON message body of the 
following format:
```python
{
  "intents": [
      {"tag": <str>, 
       "patterns": <str list>,
       "responses": <str list>},
       
      {"tag": <str>, 
       "patterns": <str list>,
       "responses": <str list>}, 
       
       ...,
       
       {"tag": <str>, 
       "patterns": <str list>,
       "responses": <str list>}
  ]
}
```
If the JSON format is incorrect, a HTTP 400 Bad Request will be raised. The response will contain information about the outcome of the new model training:
```python
{'request_info': <str>}
```

## Get Chatbot Response
Given an input query from a customer, a response from the chatbot can be obtained through the following API call:
```
/getResponse/secretkey=<str:secret_key>/modelName=<str:model_name>/message=<str:inp_message>
```
If the passed secret key is invalid or the model name does not exist, a HTTP 400 Bad Request will be raised. Else, the output will simply be the response of the chatbot. 
```python
{'chat_response': <str>} 
```
Note that if an invalid secret key is given, the chatbot response would be an empty string ('').


## Get Past Analytical Data
In addition to training models and predicting output through the ML model, the back-end stores data of all questions asked to a particular client for possible
analytics applications. To obtain all questions asked to a client in the past n days, the API call below should be made:
```
/getPastData/secretkey=<str:secret_key>/modelName=<str:model_name>/pastDays=<int:past_days>
```
The output of the API call would be a list of all questions, tags, and chatbot responses in the last 'past_days' days:
```python
[
  {'date': <datetime>,
   'question': <str>,
   'tag': <str>,
   'response': <str>},
   
   {'date': <datetime>,
   'question': <str>,
   'tag': <str>,
   'response': <str>},
  
    ...,
    
    {'date': <datetime>,
   'question': <str>,
   'tag': <str>,
   'response': <str>}
]
```

## Get Most Popular Tags
In addition to obtaining raw past analytical data on the questions asked and the corresponding tag marked by the model, the API allows you to obtain the most popular
tags in the past n days (for further analytics application). The following API call must be made:
```
/getPopularTags/secretkey=<str:secret_key>/modelName=<str:model_name>/pastDays=<int:past_days>
```
The output will be a list of tags and their corresponding count, sorted in descending order of their counts (i.e. most popular tags appear in the front of the list).
```python
[
  {'tag': <str>, 'count': <int>},
  {'tag': <str>, 'count': <int>},
  {'tag': <str>, 'count': <int>},
  ...,
  {'tag': <str>, 'count': <int>}
]
```
An example would be:
```python
[
  {'tag': 'books', 'count': 19},
  {'tag': 'food', 'count': 17},
  {'tag': 'travel', 'count': 9},
  ...,
  {'tag': 'sports', 'count': 2}
]
```