import urllib.request, requests, json, os, socket
from time import sleep

#Broadcast UDP packet using this IP and port number

#Variables that are used in functions
global UDP_PORT, UDP_IP, projectID, maskingPI
UDP_PORT = 5033 # Random UDP port selected
UDP_IP="192.168.0.255" #Broadcast address to send sockets to all Pi's
maskingPI="192.168.0.110"
projectID = ""
MESSAGE = "Catch".encode('utf-8') #encode is used because python3 requires it to send over socket
RELEASE = "Release".encode('utf-8')
MASKMSG = "Mask".encode('utf-8')

# Create the socket connection
sock = socket.socket(socket.AF_INET, 
            socket.SOCK_DGRAM) 
sock.bind(('',0))
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


def displayExistingProjects():
    
    projects = urllib.request.urlopen("http://192.168.0.100:8000/selfie/v1/projects") #get the projects

    data = json.loads(projects.read().decode()) #read the projects to display them

    print("ID \t Project Name")
    print("-------------------------------")
    for project in data:
        print(str(project['id']) + " \t " + project['name']) #display projects line by line


def addNewProject():
    name = input("Please enter the name of the project: ")
    
    #Create project where name = entered name, id is assigned through a counter via the API
    post = requests.post('http://192.168.0.100:8000/selfie/v1/projects', data = {'name': name}) 
    
    displayExistingProjects()

    print("Created successfully")


def deleteProject():
    print("Note: This will delete images in relation to project ID from the database")
    deleteID = input("What is the ID of the project you want to delete? ")

    #Deletes the project where projectID = deleteID
    post2 = requests.delete('http://192.168.0.100:8000/selfie/v1/projects/' + str(deleteID), data = {'id': deleteID})
    print (post2.text) 

    displayExistingProjects()


def postImages():
    #Looping variables
    allowCapture = True
    captureNumber = 1
    projectID = ""

    while(allowCapture):

        #Checks if project ID already has value, otherwise asks for it
        if projectID == "":
            projectID = input("\nWhat is the project ID? ")
            projectID = projectID.encode('utf-8')
            sock.sendto(projectID, (UDP_IP, UDP_PORT))


        keyInput = input("\nPress 'Enter' key to Capture, press 'r' key to release images, or press 'x' to cancel: ")

        if keyInput == "":
            #Reset the text file counter every time a capture is required
            # Send project ID to Raspberry Pi
            
            # Send catch to the Raspberry Pi
            sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

            #Receive MSG from raspberry pi(s)
            data, addr = sock.recvfrom(1024)

            print ("The packets have been sent to the listening Raspberry pi's \n Image set capture: ", captureNumber)
            captureNumber+=1

            sleep(1)
            print (data.decode('utf-8')) #print response from pi

            #receive MSG from rapsberry pi(s)
            data, addr = sock.recvfrom(1024)
            sleep(1) #Wait for image to send

            print (data.decode('utf-8')) #print response from pi
            


        elif keyInput == "r":   
            print ('Release initiated')
            print(projectID)
            sock.sendto(RELEASE, (UDP_IP, UDP_PORT))

            #Puts the project that is being released into the "ready_for_processing" queue
            update_queue =requests.put('http://192.168.0.100:8000/selfie/v1/photoscan_queues/update/' + str(projectID.decode('utf-8')), data = {'status': 'ready_for_processing'})
            print(update_queue.text)
            print ("The project " + str(projectID.decode('utf-8')) + " has been added to the queue for processing..")

            print ("Image captured has ended, please select a menu option: ")

            allowCapture = False #Ends the processing
            mainMenu()

        elif keyInput == "x":
            print("Taking processing image has been cancelled. ")
            break
            mainMenu()   

        else:
            print("Imput not valid")
            break
            mainMenu()

def createMask():

    global projectID

    #Checks if project ID already has value, otherwise asks for it
    if not projectID:
            projectID = input("\nWhat is the project ID? ")
            projectID = projectID.encode('utf-8')
            sock.sendto(projectID, (maskingPI, UDP_PORT))

    keyInput = input("\nPress 'Enter' to create mask image, or 'x' key to cancel: ")

    if keyInput == "":
        sock.sendto(MASKMSG, (maskingPI, UDP_PORT)) #Sends instruction to tell the pi to take masking pi
        sleep(1)
        jsonMsg, addr = sock.recvfrom(1024) #Receives the feedback from the 192.168.0.110 Pi
        print (jsonMsg.decode('utf-8'))


    elif keyInput == "x":
        print ("Taking mask image has been cancelled. ")


def mainMenu():    
    print("\nMain Menu")
    print("----------------------------")
    print("1. Display Existing Projects")
    print("2. Create a new Project")
    print("3. Delete project by ID")
    print("4. Create one masking Image")
    print("5. Post Images")
    print("6. Exit")

mainMenu()
menuOption = int(input("\nSelect a Menu Option: (1, 2, 3, 4, or 5): "))

#print(menuOption)

while menuOption != 6:
    
    if menuOption == 1:
        displayExistingProjects()
    elif menuOption == 2:
        addNewProject()
    elif menuOption == 3:
        deleteProject()
    elif menuOption == 4:
        createMask()
    elif menuOption == 5:
        postImages()
    elif menuOption == 6:
        exit()

    mainMenu()
    menuOption = int(input("\nSelect a Menu Option: (1, 2, 3, 4, or 5): "))
