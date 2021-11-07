#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Matthew Fong(.131)
"""
Weather Client
"""

# Still need to do! Smooth close, add logger, add arguments

from configparser import ConfigParser
from time import sleep
import sys
import socket
import string
import argparse

parser = argparse.ArgumentParser(description='Weather Client')
group = parser.add_mutually_exclusive_group(required=True)

group.add_argument(
    '-z', '--zipcode', 
    help='Added Zipcode',
    dest='zipcode',
)

group.add_argument(
    '-c', '--close', 
    help='Close the server/client', 
    dest='close_server',
    action='store_true',
    default=False
)

try:
    initial_msg, extra = parser.parse_known_args()
except:
    print("Please at least put in the minimal required arguments and try again.")
    parser.print_help()
    sys.exit()

def main(args):
    #Read config.ini file
    config_object = ConfigParser()
    config_object.read("config.ini")
    host, port = config_object['SERVERCONFIG']['host'], int(config_object['SERVERCONFIG']['port'])
  
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    # connect to server on local computer
    s.connect((host,port))
    msg = ' '.join(args)
    
    client_exit = False
    print(initial_msg)
    while not client_exit:
        if initial_msg.close_server:
            s.send(msg.encode('ascii'))
            data = s.recv(1024)
            print('Received from the server: {}'.format(str(data.decode('ascii'))))
            break
        # message sent to server
        s.send(msg.encode('ascii'))
  
        # message received from server
        data = s.recv(1024)
  
        # print the received message
        # here it would be a reverse of sent message
        print('Received from the server: {}'.format(str(data.decode('ascii'))))
  
        # ask the client whether he wants to continue
        msg = input('What else would you like to know?\n')
        try:
            args = parser.parse_known_args(msg.split())
        except:
            print("Please at least put in the minimal required arguments and try again.")
            parser.print_help()
            sys.exit()
        if '-c' in msg or '--close' in msg:
            s.send(msg.encode('ascii'))
            data = s.recv(1024)
            print('Received from the server: {}'.format(str(data.decode('ascii'))))
            client_exit = True
        if not msg:
            client_exit = True
        
        sleep(.25)

    # close the connection
    s.close()

if __name__ == "__main__":
    main(sys.argv[1:])
