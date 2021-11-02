#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Matthew Fong(.131)
"""
Weather Server
"""

from configparser import ConfigParser
import socket
import argparse
import sys

#args
parser = argparse.ArgumentParser(description='Weather Server')
parser.add_argument(
    '-z', '--zipcode', 
    help='Zip Code you want to view the weather with', 
    #required=True,
    action='append'
)

parser.add_argument(
    '-t', '--test', 
    help='Using PAM test', 
    dest='do something',
    default=False
)

args = parser.parse_args()

def main(argv):
    #Read config.ini file
    config_object = ConfigParser()
    config_object.read("config.ini")
    HOST = config_object['SERVERCONFIG']['host'] # The server's hostname or IP address
    PORT = int(config_object['SERVERCONFIG']['port']) # The port used by the server
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)

if __name__ == "__main__":
    main(sys.argv[1:])
