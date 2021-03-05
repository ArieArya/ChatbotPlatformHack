from __future__ import absolute_import
from .models import ChatbotDatabase
import os
from celery import shared_task
import json
import requests

@shared_task()
def task1():
    pass
    

@shared_task()
def task2():
    pass