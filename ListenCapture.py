from picamera import PiCamera
from time import sleep

#import time
import os
import socket
import subprocess #used to determine the IP address
import requests

UDP_PORT = 5016 #Port Chosen at random
BUFFER_SIZE = 1024

CAPTURE_PATH = '/home/pi/Documents/Image/'
IMG_FORMAT = '.jpg'

capture = True
imageCounter = 1 #used to keep track of images captured
imageCounterString = ""

#Used this line to make the Script sleep for Auto Boot testing
#sleep(1)

#Determine Pi ID - Return Pi's IP address
ip = subprocess.check_output('hostname -I', shell=True)
ip = ip.strip() #remove any white space

ip1, ip2, ip3, ip4 = ip.split('.')

#Determine text file name, for image set capture - Will be Pi IP address
filename = ip4

#Create a socket
sock = socket.socket(socket.AF_INET, # Internet
        socket.SOCK_DGRAM,
        socket.IPPROTO_UDP) # UDP

#Bind the IP Address and Port to the socket
sock.bind(('', UDP_PORT))
print"Socket Bind complete"

camera = PiCamera()

#While the user wishes to continue to capture more images
while (capture):

        print"Ready to capture images"
        projectID, addr = sock.recvfrom(BUFFER_SIZE)
        print "Project ID is: " + projectID
        data, addr = sock.recvfrom(BUFFER_SIZE) #buffer size is 1024
        #projectID, addr = sock.recvfrom(BUFFER_SIZE)
        #print addr
        print "Message received:", data
        if data=="Catch":
                print"Processing image capture please wait.."
                camera.rotation = 270

                #camera.resolution = (3280, 2464)
                camera.resolution = (1920, 1080)
		imageCounterString = str(imageCounter)
                sleep(1)

                imageTaken = CAPTURE_PATH + filename + '-' + imageCounterString + IMG_FORMAT
                #Capture the image to the directory specified above
                camera.capture(imageTaken)
                print"Image Captured"
                imageCounter += 1

                #The http directory (where images are POSTed to) is URL
                url = "http://192.168.0.100:8000/selfie/v1/" + str(projectID) + "/image"
                print "The HTTP directory is: " + url

                #Send the file taken to the HTTP directory
                files = {'url': open(imageTaken, 'rb')}
                post = requests.post(url, files=files)

                #Print the output from the PHP script
                print post.json()

	 #Release or Error Message
        elif data=="Release":
                print "Image capture ended by user - Listen script received a Release packet"
                capture = False
                imageCounter = 1
        else:
                print "Something went wrong with the packet, try again"
