"""
This module is used to test the functions of main.py
"""

import requests
import json
import sched
import time
import pyttsx3
import logging
from flask import Flask
from flask import request
from flask import render_template

from main import minutes_to_seconds
from main import hours_to_minutes
from main import hhmm_to_seconds
from main import round_to_integer
from main import news_api_request
from main import format_news_notification
from main import weather_api_request
from main import format_weather_notification
from main import covid_api_request
from main import format_covid_notification
from main import current_time
from main import tts_request
from main import create_announcment
from main import schedule_event


def test_functions() -> None:
    """this function tests all the functions in main"""
    assert minutes_to_seconds('5') == 300, 'minutes_to_seconds test: FAILED'
    #checks if minutes_to_seconds is working
    assert hours_to_minutes('5') == 300, 'hours_to_minutes test: FAILED'
    #checks if hours_to_minutes is working
    assert hhmm_to_seconds('10:15') == 36900, 'hhmm_to_seconds test: FAILED'
    #checks if hhmm_to_seconds is working
    assert round_to_integer(5.4) == 5, 'round_to_integer test: FAILED'
    assert round_to_integer(7.5) == 8, 'round_to_integer test: FAILED'
    # checks if round_to_integer is working
    api_request = news_api_request()
    assert len(api_request["articles"]) > 0, 'news_api_request test:FAILED' 
    # checks if news_api_request is working
    with open('news_test.json', 'r') as f:
        json_file = json.load(f)   
    assert format_news_notification(json_file) == {'title': 'London Covid: Why Heathrow Airport will stay open during lockdown 2 - My London', 'content': 'A small number of essential retailers and food and beverage outlets remain open at the airport'}, 'format_news_notification: FAILED'
    # checks if format_news_notification is working
    api_request = weather_api_request()
    assert api_request['cod'] == 200, 'weather_api_request test: FAILED'
    # checks if weather_api_request is working
    with open('weather_test.json', 'r') as f:
        json_file = json.load(f)
    test_value = format_weather_notification(json_file)      
    assert test_value['content'] == 'Weather: light rain. Temperature: 13°C Feels like: 12°C', 'format_weather_notification test: FAILED'
    # checks if format_weather_notification is working
    api_request = covid_api_request()
    test_value = api_request['data']
    assert len(test_value) > 1, 'covid_api_request test: FAILED'
    # checks if covid_api_request is working
    json_file = {
                    "data": [
                       {
                            "date": "2020-07-28",
                            "areaName": "England",
                            "areaCode": "E92000001",
                            "newCasesByPublishDate": "547",
                            "cumCasesByPublishDate": "259022",
                        },
                        {
                            "date": "2020-07-27",
                            "areaName": "England",
                           "areaCode": "E92000001",
                            "newCasesByPublishDate": "616",
                            "cumCasesByPublishDate": "258475",
                            "newDeathsByDeathDate": "20",
                            "cumDeathsByDeathDate": "41282"
                        },
                    ],
                    "lastUpdate": "2020-07-28T15:34:31.000000Z",
                    "length": "162",
                    "totalPages": "1"
                }
    assert format_covid_notification(json_file) == {'title': 'Covid-19 report - England 2020-07-28', 'content': "New cases today: 547 New cases yesterday: 616, Total cases: 259022, Yesterday's deaths: 20, Total deaths: 41282 Threshold level is Green - safe"}, 'format_covid_notification test: FAILED'
    # checks if format_covid_notification is working
    assert len(current_time()) == 10, 'current_time test: FAILED'
    # checks if current_time is working
    alarm = {'title': 'fun', 'content': "['2020-12-04', '10:44']", 'date': '2020-12-04', 'time': '10:44', 'news': True, 'weather': True}
    assert len(create_announcment(alarm)) == 4, 'create_announcment test: FAILED'
    {'title': 'fun', 'content': "['2020-12-04', '10:44']", 'date': '2020-12-04', 'time': '10:44', 'news': False, 'weather': False}
    assert len(create_announcment(alarm)) == 2, 'create_announcment test: FAILED'
    # checks if create_announcment is working
    






    