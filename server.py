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
arguments: void
"""
HELP_CMD='type dir to list files, exit to shutdown server'

def main():
    setup_server()

def setup_server():
    listenSocket = utils.createTcpSocket(utils.SERVER_COMM_PORT)
    listenSocket.listen(5)                           
    print('Server started listening on port ' + str(utils.SERVER_COMM_PORT));

    while True:
        connection, address = listenSocket.accept()
        print('New client connection:', address)
        while True:
            data = connection.recv(1024)
            if not data: 
                break
            connection.send(b'Echo => ' + data)   # send data using "b" to format string as byte literal (ASCII)
        connection.close()


# run main
main()