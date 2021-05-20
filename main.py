"""
This is a module that runs an interactive alarm clock that can retreive information
about the current Covid-19 crisis and can supply updates on the news and weather. 
The program uses an html application that can run as long a desired. The user can create
and delete alarms as they please using this application.
"""


import requests
import json
import sched
import time
import pyttsx3
from flask import Flask
from flask import request
from flask import render_template
import logging
s = sched.scheduler(time.time, time.sleep)
app = Flask(__name__)
logging.basicConfig(filename='pysys.log', level=logging.DEBUG)
logging.info('Log is working')
alarms = []
notifications = []

def minutes_to_seconds( minutes: str ) -> int:
    """Converts minutes to seconds"""
    return int(minutes)*60

def hours_to_minutes( hours: str ) -> int:
    """Converts hours to minutes"""
    return int(hours)*60

def hhmm_to_seconds( hhmm: str ) -> int:
    """Converts hours and minutes into seconds"""
    if len(hhmm.split(':')) != 2:
        print('Incorrect format. Argument must be formatted as HH:MM')
        return None
    return minutes_to_seconds(hours_to_minutes(hhmm.split(':')[0])) + \
        minutes_to_seconds(hhmm.split(':')[1])

def round_to_integer(number: float) -> int:
    """Round input to nearest whole number
    
    Keyword arguments:
    number -- input number to be rounded
    """
    number_value = str(number).split('.')
    decimal_value = number_value[1]
    decimal_value = list(decimal_value)
    if len(decimal_value) > 0:
        if int(decimal_value[0]) > 4: 
            number_value = int(number_value[0]) + 1
        else:
            number_value = int(number_value[0])
    else:
        number_value = int(number_value[0])
    return number_value

def news_api_request() -> dict:
    """Makes an news API request and returns info"""
    logging.info('pending news API request')
    with open('config.json', 'r') as f: #acceses config.json file
        json_file = json.load(f)
    keys = json_file["API-keys"] #API key is extracted from config.json
    api_key_news = keys["news"]
    base_url = "https://newsapi.org/v2/top-headlines?"
    country = "gb"
    complete_url = base_url + "country=" + country + "&apiKey=" + api_key_news
    response = requests.get(complete_url) #requests API information from url
    news_json = response.json()
    return news_json

def format_news_notification(api_request: dict) -> dict:
    """
    filters and formats information retreived form an API request to return a news notification
    
    Keyword arguments:
    api_request -- The information retrieved from an API request
    """
    notification ={}
    articles = api_request["articles"]
    for article in articles: #title and description of first relevant article are extracted
        source = article["source"]
        if "Covid" in article["title"]:
            notification["title"] = article["title"]
            notification["content"] = article["description"]
            break
        elif source["name"] == "BBC News":
            notification["title"] = article["title"]
            notification["content"] = article["description"]
            break
    logging.info('notification ' + notification['title'] + ' has been created')
    return notification

def check_news_api() -> dict:
    '''Makes an news API request and returns a notification
    
    Information on the latest news is requested and is then
    filtered so that only relevant articles are considered to be
    added as notifications.
    The information on the latest relevant article is returned in
    dictionary format.
    '''
    information = news_api_request()
    notification = format_news_notification(information)
    return notification
    
def weather_api_request() -> dict:
    """Makes a weather API request and returns info"""
    logging.info('pending weather API request')
    with open('config.json', 'r') as f: #Acceses config.json file
        json_file = json.load(f)
    keys = json_file["API-keys"] #API key is extracted from config.json
    api_key_weather = keys["weather"]
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city_name = json_file["location"] #Area location is extracted from config.json
    complete_url = base_url + "appid=" + api_key_weather + "&q=" + city_name
    response = requests.get(complete_url) #requests API information from url
    weather_json = response.json()
    return weather_json

def format_weather_notification(api_request: dict) -> dict:
    """
    filters and formats information retreived form an API request to return a weather notification
    
    Keyword arguments:
    api_request -- The information retrieved from an API request
    """
    notification ={}
    with open('config.json', 'r') as f: #Acceses config.json file
        json_file = json.load(f)
    city_name = json_file["location"] #Area location is extracted from config.json
    current_time_hhmm = str(time.gmtime().tm_hour) + ":" + str(time.gmtime().tm_min) #Current time is calculated
    weather = api_request["weather"] #information on weather is extracted
    weather = weather[0]
    temperature = api_request["main"]
    weather_description = weather["description"] #weather description extracted
    temperature_temp = float(temperature["temp"]) - 273.15 #temperature is extracted and rounded
    temperature_temp = round_to_integer(temperature_temp)
    # feels like temperature is extracted and rounded
    temperature_feels_like = float(temperature["feels_like"]) - 273.15 
    temperature_feels_like = round_to_integer(temperature_feels_like)
    #information is formatted into an appropriate dictionary format
    notification["title"] = 'Weather - ' + city_name + ' - ' + current_time_hhmm
    notification["content"] =("Weather: " + weather_description + ". Temperature: ") + (str(temperature_temp) + "°C Feels like: " + str(temperature_feels_like) + "°C")
    logging.info('notification ' + notification['title'] + ' has been created')
    return notification
    
def check_weather_api() -> dict:
    '''Makes a weather API request and returns a notification
    
    Information on the current weather is requested and is then
    filtered so that only weather description and temperature
    are extracted. This information is then along with the 
    current time and are name and is returned in
    dictionary format.
    '''
    information = weather_api_request()
    notification = format_weather_notification(information)
    return notification

def covid_api_request() -> dict:
    """Makes a weather API request and returns info"""
    logging.info('pending Covid-19 API request')
    from uk_covid19 import Cov19API #imports API key
    #filters are defined
    england_only = ['areaType=nation','areaName=England']
    cases_and_deaths = {
    "date": "date",
    "newCasesByPublishDate": "newCasesByPublishDate",
    "cumCasesByPublishDate": "cumCasesByPublishDate",
    "newDeathsByDeathDate": "newDeathsByDeathDate",
    "cumDeathsByDeathDate": "cumDeathsByDeathDate"}
    api = Cov19API(filters=england_only, structure=cases_and_deaths)
    covid_data = api.get_json() #requests API information
    return covid_data
    
def format_covid_notification(api_request: dict) -> dict:
    """
    Formats and computes information retreived form an API request to return a covid notification
    
    Keyword arguments:
    api_request -- The information retrieved from an API request
    """
    notification = {}
    covid_data_details = api_request["data"]
    covid_data_details_today = covid_data_details[0] 
    covid_data_details_yesterday = covid_data_details[1]
    #Threshold level is calculated
    if int(covid_data_details_today['newCasesByPublishDate']) > 10000:
        if int(covid_data_details_today['newCasesByPublishDate']) > 15000:
            threshold_level = 'Red - Not safe'
        else:
            threshold_level = 'Yellow - Be careful'
    else:
        threshold_level = 'Green - safe'
    #information is formatted into an appropriate dictionary format
    notification['title'] = "Covid-19 report - England " + covid_data_details_today['date']
    notification['content'] = ''.join(("New cases today: ", 
    str(covid_data_details_today["newCasesByPublishDate"]),
    " New cases yesterday: ",
    str(covid_data_details_yesterday["newCasesByPublishDate"]),
    ", Total cases: ",
    str(covid_data_details_today["cumCasesByPublishDate"]),
    ", Yesterday's deaths: ",
    str(covid_data_details_yesterday["newDeathsByDeathDate"]),
    ", Total deaths: ",
    str(covid_data_details_yesterday["cumDeathsByDeathDate"]), ' Threshold level is ',
    threshold_level))
    logging.info('notification ' + notification['title'] + ' has been created')
    return notification

def check_covid_api() -> dict:
    '''Makes a covid API request and returns a notification
    
    Information on the current covid cases is requested and is then
    filtered so that only relavent information is extracted.
    This information is then computed so that a threshold level
    can be calculated based on the number of cases. Threshold level
    and covid cases information are then returned in
    dictionary format.
    '''
    information = covid_api_request()
    notification = format_covid_notification(information)
    return notification


def current_time() -> str:
    """imports and formats the current date"""
    current_day = str(time.gmtime().tm_mday)
    current_month = str(time.gmtime().tm_mon)
    current_year = str(time.gmtime().tm_year)
    #adds "0"s where nessesary so that the date is readable by other functions
    if len(current_day) == 1:
        current_day = '0' + current_day
    if current_month == 1:
        current_month = '0' + current_month
    print(current_month)
    #formats the date
    return current_year + "-" + current_month + "-" + current_day

def tts_request(announcement="Text to speech example announcement!") -> None:
    """Converts text to speech
    
    Keyword arguments:
    announcement -- text that is to be converted to speech
    """
    engine = pyttsx3.init()
    engine.say(announcement)
    engine.runAndWait()
    
def create_announcment(alarm: dict) -> list:
    """Creates a list of announcements to be announcement when an alarm goes off
    
    Information is extracted from APIs and the alarm input to construct an 
    announcement based on the set alarm.
    
    Keyword arguments 
    alarm -- the alarm from where information is extracted for the announcement
    """
    logging.info('alarm ' + alarm['title'] + ' is going off')
    #information is formatted and punctionation is removed so the announcement is ready to be read
    punctuation = '!"#$%&`()*+,-./:;'
    news_announcment = (check_news_api())
    news_announcment = news_announcment['title']
    covid_announcment = check_covid_api()
    covid_announcment = covid_announcment['content']
    weather_announcement = check_weather_api()
    weather_announcement = weather_announcement['content']
    weather_announcement = weather_announcement.replace('°C', 'degrees celcius')
    for character in punctuation:
        news_announcment = news_announcment.replace(character, ' ')
        covid_announcment = covid_announcment.replace(character, ' ')
        weather_announcement = weather_announcement.replace(character, ' ')
    #the default announcement list is defined
    announcement_list = [('alarm ' + alarm['title'] + ' has gone off'), ('covid report is ' + covid_announcment)]
    #Checks if user requested new breifing
    if alarm['news'] == True:
        announcement_list.append('lastest news is ' + news_announcment)
    #Checks if user requested weather breifing
    if alarm['weather'] == True:
        announcement_list.append('weather report is ' + weather_announcement)
    #Alarm is removed from the list of set alarms after it has gone off
    if alarm in alarms:
        alarms.remove(alarm)
        logging.info('alarm ' + alarm['title'] + ' has been deleted from alarms')
    return announcement_list


def read_announcment(alarm: dict) -> None:
    """ Reads the announcement created by the create_announcment function
    
    Keyword arguments 
    alarm -- the alarm from where information is extracted for the announcement
    """
    announcement_list = create_announcment(alarm)
    for announcement in announcement_list:
        tts_request(announcement)
    #Alarm is removed from the list of set alarms after it has gone off
    if alarm in alarms:
        alarms.remove(alarm)
        logging.info('alarm ' + alarm['title'] + ' has been deleted from alarms')
    
@app.route('/')
def index():
    """The home page of the application"""
    s.run(blocking=False) #prevents scheduler from sleeping
    #renders the html template
    return render_template('index.html', title='Daily update', notifications=notifications, alarms=alarms, image='image.png')

@app.route('/index')
def schedule_event():
    """Checks for user input to set alarms and to delete alarms and notifications"""
    s.run(blocking=False) #prevents scheduler from sleeping
    alarm_details = request.args.get("alarm")
    alarm_close = request.args.get("alarm_item")
    notification_close = request.args.get("notif")
    news_briefing = request.args.get("news")
    weather_briefing = request.args.get("weather")
    #current time is calculated
    current_time_hhmm = str(time.gmtime().tm_hour) + ":" + str(time.gmtime().tm_min)
    current_time_ddmmyyyy = current_time()
    alarm_title_list = []
    current_time()
    for alarm in alarms:
        alarm_title_list.append(alarm['title'])
    if alarm_details:
        #checks for user imput and sets an alarm
        logging.info('pending atempt to create alarm')
        alarm_details = str(alarm_details)
        alarm_time = alarm_details.split('T')
        alarm_name = request.args.get("two")
        alarm = {}
        #alarm information is defined
        alarm['title'] = alarm_name
        alarm['content'] = str(alarm_time)
        alarm['date'] = alarm_time[0]
        alarm['time'] = alarm_time[1]
        if news_briefing:
            #checks if news briefing is requested
            logging.info('news briefing has been requested for alarm ' + alarm['title'])
            alarm['news'] = True
        else:    
            alarm['news'] = False
        if weather_briefing:
            #checks is weather briefing is requested
            logging.info('weather briefing has been requested for alarm ' + alarm['title'])
            alarm['weather'] = True
        else:
            alarm['weather'] = False
        if alarm['title'] not in alarm_title_list:
            #checks for duplicate alarms and schedules unique ones
            if alarm['date'] == current_time_ddmmyyyy: #checks if the alarm is to be scheduled today
                #delay is calculated and alarm is scheduled
                delay = hhmm_to_seconds(alarm['time']) - hhmm_to_seconds(current_time_hhmm)
                alarm['schedule'] = s.enter(int(delay), 1, read_announcment,(alarm,))
                logging.info('alarm ' + alarm['title'] + ' has been scheduled for ' + alarm['time'] + ' on date ' + alarm['date'])
            else:
                alarm['schedule'] = None
                logging.info('alarm ' + alarm['title'] + ' is scheduled for another day (' + alarm['date'] + ')')
                logging.info('alarm ' + alarm['title'] + ' will not be scheduled now')
            alarms.append(alarm) #alarm added to list of alarms
            logging.info('alarm "' + alarm['title'] + '" has been added to alarms')
            logging.info('alarm value is: ' + str(alarm))
        else:
            logging.warning('alarm ' + alarm['title'] + ' is a duplicate, it is not added to alarms')
    if alarm_close: #deletes an alarm if a user requests it
        logging.info('pending attempt to delete alarm')
        for i in range(len(alarms)): #searches and deletes alarm to be deleted
            alarm = alarms[i]
            if alarm["title"] == alarm_close:
                for event in s.queue: #deletes the alarm from the scheduler
                    if event == alarm['schedule']:
                        s.cancel(event)
                        logging.info('alarm ' + alarm['title'] + ' has been deleted from scheduler')
                alarms.remove(alarm) #deletes alarm from list of alarms
                logging.info('alarm ' + alarm['title'] + ' has been deleted from alarms')
                break
    if notification_close: #deletes a notification if a user requests it
        logging.info('pending attempt to delete alarm')
        for i in range(len(notifications)): #searches and deletes notification to be deleted
            notification = notifications[i]
            if notification["title"] == notification_close:
                notifications.remove(notification)
                logging.info('notification ' + notification['title'] + ' has been deleted from notifications')
                break
    return index()
    

def update_notif() -> None:
    """updates notifications every four hours"""
    s.enter(14400, 1, update_notif,())
    logging.info('notifications updating')
    notifications.append(check_news_api())
    logging.info('news notification added to notifications')
    notifications.append(check_weather_api())
    logging.info('weather notification added to notifications')
    notifications.append(check_covid_api())
    logging.info('Covid-19 notification added to notifications')
    
def update_alarm_schedule() -> None:
    """Checks when the date has changed and schedules alarms for that day"""
    s.enter(60, 1, update_alarm_schedule,())
    current_time_hhmm = str(time.gmtime().tm_hour) + ":" + str(time.gmtime().tm_min)
    if current_time_hhmm == "0:0": #checks that it's midnight
        logging.info('alarm schedule updating')
        for alarm in alarms: #searchs alarms to be scheduled for the new day
            if alarm['date'] == current_time_ddmmyyyy:
                #alarm scheduled and added to list
                delay = hhmm_to_seconds(alarm['time']) - hhmm_to_seconds(current_time_hhmm)
                alarm['schedule'] = s.enter(int(delay), 1, read_announcment,(alarm,))
                logging.info('alarm ' + alarm[title] + ' has been added to schedule')

import test_mod

if __name__ == '__main__':
    logging.info('test routine starting')
    print('test routine starting')
    try:
        test_mod.test_functions()
    except AssertionError as message:
        print(message)
        logging.warning(message)
    logging.info('test routine completed')
    #lauches the application
    s.enter(1, 1, update_notif,())
    s.enter(1, 2, update_alarm_schedule,())
    app.run()
    
