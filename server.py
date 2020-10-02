# from utils import startTerminal
import sys, getopt
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
HELP_CLI=sys.argv[0] + ' -p <server port>'
HELP_CMD='type dir to list files, exit to shutdown server'

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],'p:',["port="])
    except getopt.GetoptError:
        print(HELP_CLI)
        sys.exit(2)

    if len(opts) == 0:
        print(HELP_CLI)
        sys.exit()
    for opt, arg in opts:
        if opt in ("-p", "--port"):
            port = int(arg)
            
    if port >= 0:
        setup_server(port)


def setup_server(port):
    print('Server started on port' + str(port));

# run main
main()