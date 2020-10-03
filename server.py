# from utils import startTerminal
import os
import utils
import traceback
"""
Source: client.py
This is a terminal client for linux OS's, to transfer files across a local network

On load, the program will continuously scan and validate input.
If the user enters "start", program will enter a continous read mode, 
continuously printing out data snapshots from the GPS dongle.

At any time, the user can stop the printing by hitting "ctrl+c" in the terminal.
This stops the controlSocket with the dongle, and brings the program back to its starting state;
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
    print('Server started listening on port ', utils.SERVER_COMM_PORT);
    controlSocket = None
    try:
        controlSocket, clientIpPort = listenSocket.accept()
        isConnected=True
        clientIp = clientIpPort[0]
        print('New client:', clientIpPort)
        while isConnected:
            data = controlSocket.recv(1)
            if len(data) == 0:
                print ('client disconnected:', clientIpPort)
                isConnected=False
                break
            cmd = data.decode()
            status='Client ', clientIp, ' requested ', utils.CMDS[int(cmd)]
            print(status)

            dataSocket = utils.createTcpSocket(utils.SERVER_TX_PORT)
            dataSocket.connect((clientIp, utils.PORT_X))

            data = controlSocket.recv(3)
            msglen = int(data.decode())

            packet=''
            if cmd == utils.GETALL:
                filenames = ', '.join(os.listdir('./files'))
                packet=utils.createDataPacket(filenames) 
            elif cmd == utils.GET:
                filename=utils.recvStr(controlSocket, msglen)
                # todo, dynamic packet
            elif cmd == utils.SEND:
                pass

            utils.sendStr(dataSocket, packet)
            dataSocket.close()
            print('after shutdown')    

            # controlSocket.close()
    except KeyboardInterrupt:
        print('\nexit called.')
    except Exception as e: 
        traceback.print_exc()
    finally:
        listenSocket.close()
        if controlSocket is not None:
            controlSocket.close()
# run main
main()