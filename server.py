import os
import utils
import traceback
"""
------------------------------------------------------------------------------------------------------
SOURCE FILE: server.py - serrver application

PROGRAM: Tcp File Transfer Client Server

DATE: Oct 1, 2020

DESIGNER: Junyin Xia

PROGRAMMER: Junyin Xia

FUNCTIONS:
    void main (void)
    void handleGetAll(socket : dataSocket)
    void handleGet(socket : dataSocket, string : filename)
    void handleSend(socket : dataSocket, string : filename)

NOTES:
    This is a terminal-based fileshare server that handle client requests to transfer files of all sizes 
    both ways across a local network using TCP. On start, the server program will listen on port 7005 for clients
    Once a client connects, it continuously read and execute commands from the client.
    
    Two channels are used:
        control channel - created when a client connection is accepted, client sends commands thru this channel
            Runs between clientIp:OS port <-> serverIp:7005

        data channel - created after client issues command through control channel. the server establishes a new connection on port 7006
            on this channel to transfer file data. Runs between clientIp:8888 <-> serverIp:7006

    At any time, the user can terminate the server by hitting 'ctrl+c' (This also cleans up any sockets)
-------------------------------------------------------------------------------------------------------
"""

"""
----------------------------------------------------------------------------------------------
FUNCTION main

DATE: Oct 1 2020

DESIGNER: Junyin Xia

PROGRAMMER: Junyin Xia

INTERFACE: def main():

ARGUMENTS: void
    
RETURNS: void

NOTES:
Entry point of the server application. Main function creates the listening socket, and runs a foreverloop to 
handle client requests. It also prints client statuses.
As this is simple server, only 1 client will be handled at a time. The first client needs to disconnect before server loop
will accept any new connections. 
----------------------------------------------------------------------------------------------
"""
def main():
    listenSocket = utils.createTcpSocket(utils.SERVER_COMM_PORT)
    listenSocket.listen(5)                           
    print('Server started listening on port', utils.SERVER_COMM_PORT,'ctrl+c to exit');
    try:
        while True:
            controlSocket, clientIpPort = listenSocket.accept()
            isConnected=True
            clientIp = clientIpPort[0]
            print('New client:', clientIpPort)
            while isConnected:
                data = controlSocket.recv(1)
                if not data:
                    print ('client disconnected:', clientIpPort)
                    isConnected=False
                    continue
                cmd = data.decode()
                print('Client', clientIp, 'request', utils.CMDS[int(cmd)])

                dataSocket = utils.createTcpSocket(utils.SERVER_TX_PORT)
                dataSocket.connect((clientIp, utils.PORT_X))

                # cant use utils.readCmdPacket(controlSocket), already got 1 byte to test client connection
                msgLen=int(utils.recvStr(controlSocket,3))
                filename=utils.recvStr(controlSocket, msgLen)

                if cmd == utils.GETALL:
                    handleGetAll(dataSocket)
                elif cmd == utils.GET:
                    handleGet(dataSocket, filename)                
                elif cmd == utils.SEND:
                    handleSend(dataSocket, filename)
                dataSocket.close()
    except KeyboardInterrupt:
        print('\nexit called.')
    except Exception as e: 
        traceback.print_exc()
    finally:
        listenSocket.close()

"""
----------------------------------------------------------------------------------------------
FUNCTION handleGetAll

DATE: Oct 1 2020

DESIGNER: Junyin Xia

PROGRAMMER: Junyin Xia

INTERFACE: def handleGetAll(dataSocket):

ARGUMENTS: 
    socket dataSocket : tcp socket opened on data channel
    
RETURNS: void

NOTES:
    Handles getall requests sent from clients.
    Function reads the list of files in files dir, and sends it back to client.
----------------------------------------------------------------------------------------------
"""
def handleGetAll(dataSocket):
    filenames = '  '.join(os.listdir('./files'))
    utils.sendDataPacket(dataSocket,filenames)

"""
----------------------------------------------------------------------------------------------
FUNCTION handleGet

DATE: Oct 1 2020

DESIGNER: Junyin Xia

PROGRAMMER: Junyin Xia

INTERFACE: def handleGet(dataSocket, filename):

ARGUMENTS: 
    socket dataSocket : tcp socket opened on data channel
    string filename : file that client wants server to send back
    
RETURNS: void

NOTES:
    Handles get file requests sent from clients.
    If a requested file isnt found on server, a NOT_FOUND message is returned to the client
    Otherwise, a FOUND message + the file bytes are returned.
----------------------------------------------------------------------------------------------
"""
def handleGet(dataSocket, filename):
    if not os.path.isfile('./files/' + filename):
        utils.sendDataPacket(dataSocket, utils.NOT_FOUND)
    else:
        utils.sendDataPacket(dataSocket, utils.FOUND)
        utils.sendFile(dataSocket, filename)

"""
----------------------------------------------------------------------------------------------
FUNCTION handleSend

DATE: Oct 1 2020

DESIGNER: Junyin Xia

PROGRAMMER: Junyin Xia

INTERFACE: def handleSend(dataSocket, filename):

ARGUMENTS: 
    socket dataSocket : tcp socket opened on data channel
    string filename : file that client wants to send to server.
    
RETURNS: void

NOTES:
    Handles send file requests sent from clients.
    Reads file bytes with helper function and saves it locally, similar to what happens on client
    for GET requests
----------------------------------------------------------------------------------------------
"""
def handleSend(dataSocket, filename):
    utils.recvFile(dataSocket, filename)

# run main
main()