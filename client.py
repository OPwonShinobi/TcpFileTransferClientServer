# from utils import startTerminal
import sys
import getopt
import os
import traceback
import utils
"""
Source: client.py
This is a terminal client for linux OS's, to transfer files across a local network

On load, the program will continuously scan and validate input.
If the user enters 'start', program will enter a continous read mode, 
continuously printing out data snapshots from the GPS dongle.

At any time, the user can stop the printing by hitting 'ctrl+c' in the terminal.
This stops the connection with the dongle, and brings the program back to its starting state;
the user is once again prompted for either a 'start' or a 'exit'.

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
HELP_CLI=sys.argv[0] + ' -i <server ip>'

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],'i:',['ip='])
    except getopt.GetoptError:
        print(HELP_CLI)
        sys.exit(2)
    if len(opts) == 0:
        print(HELP_CLI)
        sys.exit()
    
    ip=''
    for opt, arg in opts:
        if opt in ('-i', '--ip'):
            ip = arg

    if ip != '':
        userInputLoop(ip)

# ip : string, ipv4 address of server
# port : int, port num server is listening on
# loop has diff get & send behaviour between server & client
def userInputLoop(ip):
    controlSocket = utils.createTcpSocket()
    try:
        controlSocket.connect((ip, utils.SERVER_COMM_PORT))
        print('Enter a command: get / get <file> / send / send <file> / exit')
        while True:
            userInput = input('>>> ')
            validInput=True
            cmd = userInput.upper()
            if cmd[0:3] == 'GET':
                filename=cmd[3:].strip()
                handleGet(controlSocket, filename)
            elif cmd[0:4] == 'SEND':
                filename=cmd[4:].strip()
                handleSend(controlSocket, filename)
            elif cmd == 'EXIT':
                print('exit called.')
                break
            else:
                validInput=False

            if not validInput:
                print('>>> Invalid input, please enter valid cmd')
    except KeyboardInterrupt:
        print('\nexit called.')
    except Exception as e: 
        traceback.print_exc()
    finally:
        controlSocket.close()

def handleGet(controlSocket, filename):
    listenSocket = utils.createTcpSocket(utils.PORT_X)
    listenSocket.listen(1)
    packet=''
    if not filename:
        utils.sendCmdPacket(controlSocket, utils.GETALL)
    else:
        utils.sendCmdPacket(controlSocket, utils.GET, filename)

    dataSocket, serverIpPort = listenSocket.accept()
    data = utils.readDataPacket(dataSocket)

    if not filename:
        # data is list of filenames
        print(data)
    else:
        # data is filename or status
        if data == utils.NOT_FOUND:
            print('File not found on server: ', filename)
        if data == utils.FOUND:
            print('Fetching', filename)
            utils.recvFile(dataSocket, filename)
    dataSocket.close()
    listenSocket.close()

def handleSend(controlSocket, filename):
    if not filename:
        print('  '.join(os.listdir('./files')))
    elif not os.path.isfile('./files/' + filename):
        print('File not found, cannot send: ', filename)
    else:
        listenSocket = utils.createTcpSocket(utils.PORT_X)
        listenSocket.listen(1)
        
        utils.sendCmdPacket(controlSocket, utils.SEND, filename)
        
        dataSocket, serverIpPort = listenSocket.accept()
        utils.sendFile(dataSocket, filename)
        
        print('File sent to server')
# run main
main()