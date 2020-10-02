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
# Function: start_terminal
# Designer: Alex Xia
# Programmer: ALex Xia
# Date: Oct 1 2020
# 
# Bring program into state which waits for user input
def startTerminal():
    waitForUserInput()

# Function: start_terminal
# Designer: Alex Xia
# Programmer: Keir Forster
# Date: Nov 4 2017
# 
# Starts the loop which prompts and checks for user input.
# Then depending on input('start' or 'exit') calls related GPS connection function
def waitForUserInput():
    printWelcomePrompt(True)
    while True:
        try:
            userInput = input(">>> ")
            validInput=True
            if userInput.isalpha():
                cmd = userInput.upper()
                if cmd == "GET":
                    pass
                elif cmd == "SEND":
                    pass    
            else:
                validInput=False
            
            if not validInput:
                print(">>> Invalid input, please enter valid cmd")
            
        except KeyboardInterrupt:
            print("\n")
            printWelcomePrompt(False)    
        except Exception as e: 
            print("Warning: " + str(e))
            printWelcomePrompt(False)    

# Function: printWelcomePrompt
# Designer: Alex Xia
# Programmer: Alex Xia
# Date: Nov 4 2017
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
