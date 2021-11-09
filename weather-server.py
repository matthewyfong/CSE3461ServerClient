#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Matthew Fong(.131)
"""
Weather Server
https://openweathermap.org/api
"""

from configparser import ConfigParser
import io
import sys
import socket
import argparse
from time import sleep
import threading
import requests
import json
import logging

#args
parser = argparse.ArgumentParser(description='Weather Server')
group = parser.add_mutually_exclusive_group(required=False)

parser.add_argument(
    '-c', '--close', 
    help='Close the server/client', 
    dest='close_server',
    action='store_true',
    default=False
)

parser.add_argument(
    '-z', '--zipcode', 
    help='Added Zipcode',
    dest='zipcode',
)

group.add_argument(
    '-w', '--windspeed', 
    help='Show windspeed', 
    dest='windspeed',
    action='store_true',
    default=False
)

group.add_argument(
    '-y', '--humidity', 
    help='Show humidity', 
    dest='humidity',
    action='store_true',
    default=False
)

group.add_argument(
    '-t', '--temperature', 
    help='Show temperature', 
    dest='temp',
    action='store_true',
    default=False
)

group.add_argument(
    '-l', '--highlow', 
    help='Show high/low', 
    dest='highlow',
    action='store_true',
    default=False
)

group.add_argument(
    '-p', '--precipitation', 
    help='Show percipitation', 
    dest='precipitation',
    action='store_true',
    default=False
)

logging.basicConfig(filename='weather.log', filemode='w', encoding='utf-8', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
print_lock = threading.Lock()
WEATHER_API_KEY = "b8672eafc859e96de4c67b74b9680e71"
true_exit = False

def apiWeather(zipcode):
    logging.info('Making API Request for current weather')
    response = requests.get('https://api.openweathermap.org/data/2.5/weather?zip={}&appid={}&units=imperical'.format(zipcode, WEATHER_API_KEY))
    return response
    
def apiThreeHour(zipcode):
    logging.info('Making API Request for future weather')
    response = requests.get('https://api.openweathermap.org/data/2.5/forecast?zip={}&appid={}&units=imperical'.format(zipcode, WEATHER_API_KEY))
    return response

# https://www.weather.gov/mlb/seasonal_wind_threat
def getWindspeed(zipcode, responseCurrent):
    data = responseCurrent.json()
    windCurrently = data['wind']['speed']
    logging.info('Getting wind conditions message for printing.')
    message = "The current windspeed at {} is {} mph.".format(zipcode, windCurrently)
    if windCurrently < 10:
        message += 'The sustain wind speeds are non-threatening; "breezy" conditions may still be present.'
    elif 10 <= windCurrently < 20:
        message += '"Breezy" to "Windy" conditions. Sustained wind speeds around 20 mph, or frequent gusts of 25 to 30 mph.'
    elif 20 <= windCurrently < 25:
        message += '"Windy" conditions. Sustained wind speeds of 21 to 25 mph, or frequent wind gusts of 30 to 35 mph.'
    elif 25 <= windCurrently < 39:
        message += '"Very windy" with sustained speeds of 26 to 39 mph, or frequent wind gusts of 35 to 57 mph. Wind conditions consistent with a wind advisory.'
    elif 39 <= windCurrently < 57:
        message += '"High wind" with sustained speeds of 40 to 57 mph. Wind conditions consistent with a high wind warning.'
    else:
        message += '"Damaging high wind" with sustained speeds greater than 58 mph, or frequent wind gusts greater than 58 mph. Damaging wind conditions are consistent with a high wind warning.'
    return message
    
def getHumidity(zipcode, responseCurrent):
    data = responseCurrent.json()
    logging.info('Getting humidity message for printing')
    humidityCurrently = data['main']['humidity']
    message = "The current humidity at {} is {}%.".format(zipcode, humidityCurrently)
    return message
    
def getTemp(zipcode, responseCurrent):
    data = responseCurrent.json()
    logging.info('Getting temperature message for printing')
    tempCurrently = data['main']['temp']
    message = "The current temperature at {} is {} Kelvin.".format(zipcode, tempCurrently)
    return message

def getHighLow(zipcode, responseCurrent):
    data = responseCurrent.json()
    logging.info('Getting high/low message for printing')
    minCurrently = data['main']['temp_min']
    maxCurrently = data['main']['temp_max']
    message = "The current min at {} is {} Kelvin.".format(zipcode, minCurrently)
    message += "The current min at {} is {} Kelvin.".format(zipcode, maxCurrently)
    return message
    
def getPrecipitation(zipcode, responseFuture):
    data = responseFuture.json()
    logging.info('Getting precipitation message for printing')
    rainThreeHours = []
    rainThreeHours = data['list']
    rain = 0
    for time in rainThreeHours:
        if rain in time:
            rain += time['rain']['3h']
    message = "The expected rain in the next 3 hours at {} is {} mm.".format(zipcode, rain)
    return message
  
# thread function
def threaded(c, port):
    global true_exit
    logging.info('Starting new thread')
    thread_exit = False
    while not thread_exit:
        # data received from client
        logging.info('Receiving from client')
        data = c.recv(1024).decode('ascii')
        if data:
            logging.info('Resetting stdout to variable')
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout
            try:
                logging.info('Parsing user sent arguments')
                args = parser.parse_args(data.split())
            except:
                logging.warning('Exception found, printing help message')
                print("Something went wrong; here's some help.")
                parser.print_help()
                logging.info('Changing stdout to i/o interface')
                message = new_stdout.getvalue()
                sys.stdout = old_stdout
                print("{}".format(message))
                logging.info('Sending message back to client')
                c.send(new_stdout.getvalue().encode('ascii'))
                continue
            if args.close_server:
                logging.info('Setting variables to close server')
                true_exit = True
                thread_exit = True
                print("Shutting down now!")
            else:
                responseCurrent = apiWeather(args.zipcode)
                responseFuture = apiThreeHour(args.zipcode)
                if not args.windspeed and not args.humidity and not args.temp and not args.highlow and not args.precipitation: #and args.
                    logging.info('No arguments found')
                    print("You need something to check!")
                    parser.print_help()
                else:
                    if args.windspeed:
                        print(getWindspeed(args.zipcode, responseCurrent))
                    if args.humidity:
                        print(getHumidity(args.zipcode, responseCurrent))
                    if args.temp:
                        print(getTemp(args.zipcode, responseCurrent))
                    if args.highlow:
                        print(getHighLow(args.zipcode, responseCurrent))
                    if args.precipitation:
                        print(getPrecipitation(args.zipcode, responseFuture))
            logging.info('Changing stdout to i/o interface')
            message = new_stdout.getvalue()
            sys.stdout = old_stdout
            print("{}".format(message))
            logging.info('Sending message back to client')
            c.send(new_stdout.getvalue().encode('ascii'))
        else:
            logging.info('Client closing itself')
            print('Bye')
            c.send("Good bye!".encode('ascii'))
            break
        sleep(.25)
            
    # lock released on exit
    print("Closing thread.")
    print_lock.release()
    # connection closed
    c.close()
  
def main(args):
    logging.info('Server starting up')
    thread_count = 0
    #Read config.ini file
    logging.info('Reading config file')
    config_object = ConfigParser()
    config_object.read("config.ini")
    
    logging.info('Performing socket work')
    host, port = config_object['SERVERCONFIG']['host'], int(config_object['SERVERCONFIG']['port'])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port))
    except socket.error as e:
        logging.error(e)
        print(str(e))
    print("socket binded to port", port)
  
    # put the socket into listening mode
    s.listen()
    print("socket is listening")
  
    # a forever loop until client wants to exit
    while not true_exit:
        # establish connection with client
        c, addr = s.accept()
        logging.info('Accepted client')
        # lock acquired by client
        print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])
        data = c.recv(1024).decode('ascii')
        c.send("Connected to : {} : {}".format(addr[0], addr[1]).encode('ascii'))
  
        # Start a new thread and return its identifier
        t = threading.Thread(target=threaded, args=(c, addr[1]))
        t.start()
        t.join()
    logging.info('Closing socket and exiting')
    s.close()

if __name__ == "__main__":
    main(sys.argv[1:])
