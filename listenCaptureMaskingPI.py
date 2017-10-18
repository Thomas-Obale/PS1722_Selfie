from picamera import PiCamera
from time import sleep
import shutil,  os, socket, subprocess, requests

UDP_PORT = 5033 #Port Chosen at random
BUFFER_SIZE = 1024

CAPTURE_PATH = '/home/pi/Documents/Image/'
IMG_FORMAT = '.jpg'
PC_IP = "pi3d.scem.ws"
capture = True
imageCounter = 1 #used to keep track of images captured
imageCounterString = ""

#Determine Pi ID - Return Pi's IP address
ip = subprocess.check_output('hostname -I', shell=True)
ip = ip.strip() #remove any white space

ip1, ip2, ip3, ip4 = ip.split('.')

#Determine photo file name - Will be Pi IP address last octet
filename = ip4

#Create a socket - used to create a link and send packets over the network
sock = socket.socket(socket.AF_INET, # Internet
        socket.SOCK_DGRAM,
        socket.IPPROTO_UDP) # UDP

#Bind the IP Address and Port to the socket
sock.bind(('', UDP_PORT))
print"Socket Bind complete"

camera = PiCamera() #Declare camera
projectID = ""
#While the user wishes to continue to capture more images
while (capture):

        print"Ready to capture images"
	#this is to prevent project ID being entered from the instruction packet
        if (len(projectID) ==  0):
		projectID, addr = sock.recvfrom(BUFFER_SIZE) #Receive project ID packet from usingRequest.py        
		print "Project ID is: " + projectID + " i am here" 
	
	#Receive instruction (catch or release) from the manager.py
        instruction, addr = sock.recvfrom(BUFFER_SIZE) #buffer size is 1024

        print "Message received:", instruction
        if instruction=="Catch":
                print"Processing image capture please wait.."
                camera.rotation = 270

                camera.resolution = (3280, 2464)
                #camera.resolution = (1920, 1080)
		imageCounterString = str(imageCounter)
                sleep(1)

                imageTaken = CAPTURE_PATH + filename + '-' + imageCounterString + IMG_FORMAT
                #Capture the image to the directory specified above
                camera.capture(imageTaken)
                PC_MSG = "Image Captured " + "from: " + ip 
		print addr
		print PC_MSG
                imageCounter += 1
		
		sock.sendto(PC_MSG, addr)		
                #The http directory (where images are POSTed to) is URL
                url = "http://pi3d.scem.ws/selfie/v1/" + str(projectID) + "/image"
                print "The HTTP directory is: " + url
		
                #Send the file taken to the HTTP directory
                files = {'url': open(imageTaken, 'rb')}
                post = requests.post(url, files=files, data = {'type': 'processing_image'})

                #Print the output from the PHP script and send to manager.py
		jsonMsg = post.json()
                print jsonMsg

		sock.sendto(jsonMsg, addr)

	 #Release or Error Message
        elif instruction=="Release":
                print "Image capture ended by user - Listen script received a Release packet"
                #remove the /Documents/Image/ directory and re-create it - this is to delete old photos
                #that are no longer required to be stored locally
                if os.path.exists(CAPTURE_PATH):
                        print("Removing " + CAPTURE_PATH)    
                        shutil.rmtree(CAPTURE_PATH)
                #Create new /Documents/Image/ directory to replace the deleted one
                os.mkdir(CAPTURE_PATH)
                
	elif instruction=="Mask":
		print projectID
		camera.rotation = 270
		camera.resolution = (3280, 2464)
		sleep(1)
		#Sets the mask directory for the photo to be taken and POSTed from
		maskDirectory = CAPTURE_PATH + "mask" + "P_ID" + projectID + IMG_FORMAT
		camera.capture(maskDirectory)
		
		url = "http://pi3d.scem.ws/selfie/v1/" + str(projectID) + "/image"
		
		#Send the mask to the corresponding project ID database
		files = {'url': open(maskDirectory, 'rb')}
		post = requests.post(url, files=files, data = {'type': 'masking_image'})
                
		#Send JSON msg to the manager.py script
		jsonMsg = post.text
		print jsonMsg
		sock.sendto(jsonMsg, addr)
