import socket
import os

"""
------------------------------------------------------------------------------------------------------
SOURCE FILE: utils.py - shared code between server & client application

PROGRAM: Tcp File Transfer Client Server

DATE: Oct 1, 2020

DESIGNER: Junyin Xia

PROGRAMMER: Junyin Xia

FUNCTIONS:
    void main (void)
    void userInputLoop(string : ip)
    void handleGet(socket : controlSocket, string : filename)
    void handleSend(socket : controlSocket, string : filename)

GLOBAL CONSTANTS:
    ports
        int SERVER_COMM_PORT=7005 : control channel server port, client port is dynamic
        int SERVER_TX_PORT=7006 : data channel server port 
        int PORT_X=8888 : data channel client port 

    flag, all saved in string form to avoid calling str(flag)
        string GETALL='0'
        string GET='1'
        string SEND='2'
        tuple CMDS=('GETALL','GET','SEND') : list for getting string form of flags from int, eg CMD[int(GETALL)]='GETALL'

    status
        string NOT_FOUND='/404/' : msg the server sends to client when requested file not found 
        string FOUND='/200/' : msg the server sends to client when requested file found
    
    misc    
        int BUFFER_SIZE=8192 : max number of bytes (8kb) to read at a time from either a socket or a file

NOTES:
    This file contains helper functions shared between server & client.
-------------------------------------------------------------------------------------------------------
"""



SERVER_COMM_PORT=7005
SERVER_TX_PORT=7006
PORT_X=8888

GETALL='0'
GET='1'
SEND='2'
CMDS=('GETALL','GET','SEND')

NOT_FOUND='/404/'
FOUND='/200/'
BUFFER_SIZE=8192

"""
----------------------------------------------------------------------------------------------
FUNCTION createTcpSocket

DATE: Oct 1 2020

DESIGNER: Junyin Xia

PROGRAMMER: Junyin Xia

INTERFACE: def createTcpSocket(bindPort=None):
    
ARGUMENTS: int bindPort : port to bind new socket to, leave empty to use random port assigned by OS 

RETURNS: void

NOTES:
Creates a new TCP socket, and binds it to a local port if specified.
Also sets the socket address to be reusable.
----------------------------------------------------------------------------------------------
"""
def createTcpSocket(bindPort=None):
    newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    newSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if bindPort is not None:
        newSocket.bind(('', bindPort))
    return newSocket


"""
----------------------------------------------------------------------------------------------
FUNCTION sendStr

DATE: Oct 1 2020

DESIGNER: Junyin Xia

PROGRAMMER: Junyin Xia

INTERFACE: def sendStr(sendSocket,str):
    
ARGUMENTS:
    socket sendSocket : socket to send strings from
    string str : string message to send

RETURNS: void

THROWS
    RuntimeError if socket disconnects while sending

NOTES:
    A wrapper function for python's socket.send(bytes). Converts string message to bytes, and sends it across a socket.
    Due to nature of network buffers, python's socket.send may need to be called multiple times to make sure all bytes are sent,
    especially sending longer messages. 

    Before calling this, the message length should already be sent to otherside 
----------------------------------------------------------------------------------------------
"""
def sendStr(sendSocket,str):
    total_sent = 0
    total = len(str)
    byte_str = str.encode()
    while total_sent < total:
        bytes_sent = sendSocket.send(byte_str[total_sent:])
        if bytes_sent == 0:
            raise RuntimeError("sendStr socket disconnected")
        total_sent += bytes_sent

"""
----------------------------------------------------------------------------------------------
FUNCTION recvStr

DATE: Oct 1 2020

DESIGNER: Junyin Xia

PROGRAMMER: Junyin Xia

INTERFACE: def recvStr(recvSocket,msgLen):
    
ARGUMENTS:
    socket recvSocket : socket to send strings from
    int msgLen : string message to send

RETURNS: string - msgLen sized msg that was read from socket

THROWS
    RuntimeError if socket disconnects before all bytes are read

NOTES:
    A wrapper function for python's socket.recv(bytes). Reads BUFFER_SIZE bytes from socket at a time, and keep reading until expected size reached.
    Due to nature of network buffers, python's socket.recv may not read all the bytes on the socket in 1 call. 
    especially when receiving longer messages. That is why client & server uses this wrapper for anything longer than a couple bytes.

    If msgLen isn't known (3 for cmd or data packet), before calling this to get message, should call recvStr(recvSocket,3) to get message length first
----------------------------------------------------------------------------------------------
"""
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

"""
----------------------------------------------------------------------------------------------
FUNCTION sendCmdPacket

DATE: Oct 1 2020

DESIGNER: Junyin Xia

PROGRAMMER: Junyin Xia

INTERFACE: def sendCmdPacket(sendSocket,flag,msg=''):
    
ARGUMENTS:
    socket sendSocket : socket to send packet to
    string flag : one of the global command flags, GET/GETALL/SEND
    msg : string message to send with packet, empty by default

RETURNS: void

NOTES:
    Constructors a packet (string) like so
    [flag][length of msg][msg]
    1 byte  3 bytes
    Then calls sendStr to send packet to socket
----------------------------------------------------------------------------------------------
"""
def sendCmdPacket(sendSocket,flag,msg=''):
    msgStr=str(msg)
    paddedLength = '{:0>3}'.format(len(msgStr))
    packet=flag + paddedLength + msgStr
    sendStr(sendSocket, packet)

"""
----------------------------------------------------------------------------------------------
FUNCTION readCmdPacket

DATE: Oct 1 2020

DESIGNER: Junyin Xia

PROGRAMMER: Junyin Xia

INTERFACE: def readCmdPacket(readSocket):
    
ARGUMENTS:
    socket readSocket : socket to read from

RETURNS: 
    flag : string flag command, one of GET/GETALL/SEND
    msg : usually the requested file's name, for GETALL this is empty 

NOTES:
    Read some bytes from a socket, in this format
    [flag][length of msg][msg]
    1 byte  3 bytes
    then returns the flag and decoded string.
    See readDataPacket header for why it's used here
----------------------------------------------------------------------------------------------
"""
def readCmdPacket(readSocket):
    flag =recvStr(readSocket,1)
    msg = readDataPacket(readSocket)
    return (flag, msg)

"""
----------------------------------------------------------------------------------------------
FUNCTION sendDataPacket

DATE: Oct 1 2020

DESIGNER: Junyin Xia

PROGRAMMER: Junyin Xia

INTERFACE: def sendDataPacket(sendSocket, msg):
    
ARGUMENTS:
    socket sendSocket : socket to send msg from
    string msg : message to send as part of packet

RETURNS: void

NOTES:
    Send some bytes to a socket, in this format
    [length of msg][msg]
      3 bytes       N bytes
    This is same format has cmdPacket, minus the flag 1 byte.
----------------------------------------------------------------------------------------------
"""
def sendDataPacket(sendSocket, msg):
    msgStr=str(msg)
    paddedLength = '{:0>3}'.format(len(msgStr))
    packet=paddedLength + msgStr
    sendStr(sendSocket, packet)

"""
----------------------------------------------------------------------------------------------
FUNCTION readDataPacket

DATE: Oct 1 2020

DESIGNER: Junyin Xia

PROGRAMMER: Junyin Xia

INTERFACE: def readDataPacket(readSocket):
    
ARGUMENTS:
    socket readSocket : socket to read from

RETURNS: string : string message that was read from socket

NOTES:
    Read some bytes from a socket, in this format
    [length of msg][msg]
           3 bytes  N bytes
    then returns the decoded msg.
----------------------------------------------------------------------------------------------
"""
def readDataPacket(readSocket):
    msgLen=int(recvStr(readSocket,3))
    return recvStr(readSocket, msgLen)

"""
----------------------------------------------------------------------------------------------
FUNCTION sendFile

DATE: Oct 1 2020

DESIGNER: Junyin Xia

PROGRAMMER: Junyin Xia

INTERFACE: def sendFile(sendSocket,filename):
    
ARGUMENTS:
    socket sendSocket : socket to send file to
    string filename : file to read & send 

RETURNS: void

NOTES:
    This function does not check if file exist, server.handleGet & client.handleSend functions already handles it. 
    Writes a file to a socket chunk by chunk. 

    Open a file in binary mode, and send its filesize as a data packet
        packet1 - [size of filesize str][filesize as str]
                    3 bytes                 N bytes
    If file isn't empty, read the file BUFFER_SIZE chunks at a time, and send each chunk across sendSocket
    (Untested, but in theory, since file is read & transferred 1 BUFFER_SIZE chunk at a time, any sized file can be sent.)
----------------------------------------------------------------------------------------------
"""
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

"""
----------------------------------------------------------------------------------------------
FUNCTION recvFile

DATE: Oct 1 2020

DESIGNER: Junyin Xia

PROGRAMMER: Junyin Xia

INTERFACE: def sendFile(sendSocket,filename):
    
ARGUMENTS:
    socket sendSocket : socket to send file to
    string filename : file to read & send 

RETURNS: void

NOTES:
    Counterpart to sendFile, reads a file chunk by chunk from a socket and saves it.
    
    Creates or clears a file locally with filename passed in. Then reads the file size from the socket, and reads the 
    file chunk by chunk from the socket if it isn't empty.

    (Untested, but in theory, since file is read & saved 1 BUFFER_SIZE chunk at a time, any sized file can be received.)
----------------------------------------------------------------------------------------------
"""
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
