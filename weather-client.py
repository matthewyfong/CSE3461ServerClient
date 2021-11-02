#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Matthew Fong(.131)
"""
Weather Client
"""

from configparser import ConfigParser
import socket
import argparse
import sys

#args
parser = argparse.ArgumentParser(description='Weather Client')
parser.add_argument(
    '-z',
    '--zipcode', 
    help='Zip Code you want to view the weather with', 
    dest='zip',
    #required=True,
    action='append'
)

parser.add_argument(
    '-a', '--added', 
    help='Added asset files', 
    dest='do something',
    type=str, 
    default=""
)

args = parser.parse_args()

def main(argv):
    #Read config.ini file
    config_object = ConfigParser()
    config_object.read("config.ini")
    HOST = config_object['SERVERCONFIG']['host'] # The server's hostname or IP address
    PORT = int(config_object['SERVERCONFIG']['port']) # The port used by the server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b'Hello, world')
        data = s.recv(1024)

    print('Received', repr(data))

if __name__ == "__main__":
    main(sys.argv[1:])

