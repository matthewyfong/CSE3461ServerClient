#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Matthew Fong(.131)
"""
Config Creater
"""

from configparser import ConfigParser
import argparse
import sys

# Get the configparser object
config_object = ConfigParser()

#args
parser = argparse.ArgumentParser(description='Weather Server')
parser.add_argument(
    '-t', '--host', 
    help='Enter a valid host number', 
    required=True,
)

parser.add_argument(
    '-p', '--port', 
    help='Enter a valid port number > 1023', 
    required=True,
)

args = parser.parse_args()

def main(argv):
    # Create Config File for Clinet/Server to read.
    config_object["SERVERCONFIG"] = {
        "HOST": "{}".format(args.host),
        "PORT": "{}".format(args.port)
    }

    #Write the above sections to config.ini file
    with open('config.ini', 'w') as conf:
        config_object.write(conf)
    
if __name__ == "__main__":
    main(sys.argv[1:])