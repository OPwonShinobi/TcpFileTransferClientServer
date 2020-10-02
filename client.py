# from utils import startTerminal
import sys, getopt
import utils
"""
Source: client.py
This is a terminal client for linux OS's, to transfer files across a local network

On load, the program will continuously scan and validate input.
If the user enters "start", program will enter a continous read mode, 
continuously printing out data snapshots from the GPS dongle.

At any time, the user can stop the printing by hitting "ctrl+c" in the terminal.
This stops the connection with the dongle, and brings the program back to its starting state;
the user is once again prompted for either a "start" or a "exit".

On receiving user input to exit, the program will terminate.

Functions: main

Date: Oct 1 2020
Designer: Alex Xia
Programmer: Alex Xia

"""

"""
Function: main
returns: void
arguments: string[] argv - string array of command line arguments
"""
HELP_CLI=sys.argv[0] + ' [-h] -i <server ip>'
HELP_CMD='type dir to list files, exit to shutdown client'

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],'i:',["ip="])
    except getopt.GetoptError:
        print(HELP_CLI)
        sys.exit(2)
    if len(opts) == 0:
        print(HELP_CLI)
        sys.exit()
    
    ip=''
    for opt, arg in opts:
        if opt in ("-i", "--ip"):
            ip = arg

    if ip != '':
        setup_client(ip)
    else:
        print("Please enter server ip: " + ip);


def setup_client():
    pass
# run main
main()