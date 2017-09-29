import socket
import os
import sys
import requests
from time import sleep

#Broadcast UDP packet using this IP and port number
UDP_IP="192.168.0.255"
UDP_PORT = 5016 # Random UDP port selected

MESSAGE = "Catch"
RELEASE = "Release"
CAMERA_NUM = 9
projectID = ""

#UDP IP and Socket settings here
print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE

# Create the socket connection
sock = socket.socket(socket.AF_INET, 
			socket.SOCK_DGRAM) 
sock.bind(('',0))
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

txtFilePath = '/Users/user/Desktop/pushImage/.'

projectID = raw_input("Please Enter project ID: ")

#Looping variables
allowCapture = True
captureNumber = 1

while(allowCapture):
    txtCount = 0
    keyInput = raw_input("\nEnter to Capture, or R key to release images: ")
    if keyInput=="":
        #Reset the text file counter every time a capture is required
        # Send project ID to Raspberry Pi
        sock.sendto(projectID, (UDP_IP, UDP_PORT))
        # Send a message to the Raspberry Pi
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))


        print "Image set capture: ", captureNumber
        captureNumber+=1

        
        """#Check if there are more text files that indicate complete transfer, than there should be
        #Too many images in the PushImage means something went wrong when moving / transferring image files
        if (txtCount>CAMERA_NUM):
            print('number of text files found: ' + str(txtCount))
            print('Something went wrong, there are too many image files possibly due to a delay in the network. \nPlease try again')
            
            #Reset the counters on each Pi, before exiting this script.
            sock.sendto(RELEASE, (UDP_IP, UDP_PORT))
            
            #Exit the script
            sys.exit("Exiting send.py script")
            """

    elif keyInput=="r":
	print ('Release initiated')
        sock.sendto(RELEASE, (UDP_IP, UDP_PORT))
   
        allowCapture = False
        print "The script has ended."

    else:
        print "Something went wrong with the sending packet"

