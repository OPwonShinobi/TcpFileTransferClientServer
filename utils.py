import socket
import os

"""
Source: utils.py

This is the heart and lungs of this gpsd client.
The GPSD daemon is called via a python interface, gps3, 
On load, program enters a loop, waiting for and checking user input.
If user enters start, program will enter a continuous read mode, and try to call the gspd daemon for
a host and a port (the defaults are host=127.0.0.1, port=2947).

If a connection with a GPS dongle is successful, program enters a loop waiting for and 
printing any satellite data coming in through the gpsd daemon.    

The user can cancel the connection at any time, program returns to user input loop, until
user calls the program to exit.

Functions: 
    startTerminal() : void
    waitForUserInput() : void
    printWelcomePrompt(firstRun=True) : void
    continuousRead() : void

Date: Oct 1 2020
Designer: Alex Xia
Programmer: Alex Xia       
"""

SERVER_COMM_PORT=7005
SERVER_TX_PORT=7006
PORT_X=8888

# flags, strings used so dont have to call str on it every time
GETALL='0'
GET='1'
SEND='2'
CMDS=('GETALL','GET','SEND')

# misc
NOT_FOUND='/404/'
FOUND='/200/'
BUFFER_SIZE=8192

# Function: printWelcomePrompt
# Designer: Alex Xia
# Programmer: Alex Xia
# Date: Oct 1 2020
# Arguments: firstRun - boolean which determines if 
#              it's user's first time running application
# 
# Prints pseudo-UI user instructions specific to if user has or hasn't start
# completed a gps connection during life of program.

def printWelcomePrompt(firstRun):
    if firstRun:
        print("*{:*<70}*".format("*"))
        print("* {:<69}*".format("A dumb GPS terminal program."))
        print("* {:<69}*".format("Enter 'start' to start reading from your GPS"))
        print("* {:<69}*".format("Enter 'exit' to exit this application"))
        print("* {:<69}*".format("Or, press the hotkey 'Ctrl+c' to stop a running connection."))
        print("*{:*<70}*".format("*"))
    else:
        print("*{:*<70}*".format("*"))
        print("* {:<69}*".format("connection ended."))
        print("* {:<69}*".format("Enter 'start' to restart reading from your GPS"))
        print("* {:<69}*".format("Enter 'exit' to exit this application"))
        print("* {:<69}*".format("Or, press the hotkey 'Ctrl+c' to stop a running connection."))
        print("*{:*<70}*".format("*"))


def createTcpSocket(bindPort=None):
    newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    newSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if bindPort is not None:
        newSocket.bind(('', bindPort))
    return newSocket

# They do not necessarily handle all the bytes you hand them (or expect from them),
#  In general, they return when the associated network buffers have been filled (send) or emptied (recv). They then tell you how many bytes they handled. It is your responsibility to call them again until your message has been completely dealt with.
def sendStr(sendSocket,str):
    total_sent = 0
    total = len(str)
    byte_str = str.encode()
    while total_sent < total:
        bytes_sent = sendSocket.send(byte_str[total_sent:])
        if bytes_sent == 0:
            raise RuntimeError("sendStr socket disconnected")
        total_sent += bytes_sent

# we can get away with read chunk == 0 here cause short msges, prob wont get delay
def recvStr(recvSocket,msgLen):
    chunks = []
    bytes_read = 0
    while bytes_read < msgLen:
        chunk = recvSocket.recv(min(BUFFER_SIZE,msgLen))
        # python empty str is false, empty chunk == connection broke, stop reading
        if not chunk:
            raise RuntimeError('recvStr socket disconnected while reading!')
        chunks.append(chunk)
        bytes_read += len(chunk)
    return b''.join(chunks).decode()


def sendCmdPacket(sendSocket,flag,msg=''):
    msgStr=str(msg)
    paddedLength = '{:0>3}'.format(len(msgStr))
    packet=flag + paddedLength + msgStr
    sendStr(sendSocket, packet)

def readCmdPacket(readSocket):
    flag =recvStr(readSocket,1)
    msg = readDataPacket(readSocket)
    return (flag, msg)

def sendDataPacket(sendSocket, msg):
    msgStr=str(msg)
    paddedLength = '{:0>3}'.format(len(msgStr))
    packet=paddedLength + msgStr
    sendStr(sendSocket, packet)

def readDataPacket(readSocket):
    msgLen=int(recvStr(readSocket,3))
    return recvStr(readSocket, msgLen)

# does not check file exist!, thats handled in handleGet & handleSend methods
# cannot use file.read as we dont know/care about file size. Prog should work regardless of filesize
def sendFile(sendSocket,filename):
    # read binary mode
    with open('./files/'+filename,'rb') as file:
        filesize=os.path.getsize('./files/'+filename)
        
        sendDataPacket(sendSocket, filesize)
        if filesize != 0:
            bytes_sent=0
            while bytes_sent < filesize:
                chunk=file.read(BUFFER_SIZE)
                if not chunk:
                    raise RuntimeError("sendFile socket disconnected while sending")
                bytes_sent+=sendSocket.send(chunk)
        print('File sent, bytes',filesize)

def recvFile(recvSocket,filename):
    filesize=int(readDataPacket(recvSocket))

    # create or clear file
    with open('./files/'+filename,'w') as file:
        file.write('')
        
    print('Sender\'s file size: ',filesize)
    if filesize == 0:
        return

    with open('./files/'+filename,'ab') as file:
        bytes_read = 0
        while bytes_read < filesize:
            chunk = recvSocket.recv(BUFFER_SIZE)
            if not chunk:
                print('recvFile socket disconnected while reading!')
                break
            file.write(chunk)
            bytes_read += len(chunk)
    print('File saved: /files/'+filename)
