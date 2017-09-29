import urllib.request, requests, json, os


def displayExistingProjects():
    
    projects = urllib.request.urlopen("http://localhost:8000/selfie/v1/project")

    data = json.loads(projects.read().decode())

    print("ID \t Project Name")
    print("-------------------------------")
    for project in data:
        print(str(project['id']) + " \t " + project['name'])



def addNewProject():
    name = input("Please enter the name of the project")
    
    post = requests.post('http://localhost:8000/selfie/v1/project', data = {'name': name})
    
    displayExistingProjects()

    print("Created Successfully")


def postImages():
    print("\nSelect Project by ID to post images to")
    displayExistingProjects()

    id = int(input("Select project ID "))a

    for (dirname, dirs, files) in os.walk('images'):
        for filename in files:
            if filename.endswith('.jpg') :
                url = "http://localhost:8000/selfie/v1/" + str(id) + "/image"
                files = {'url': open(dirname + "/" + filename, 'rb')}
                requests.post(url, files=files)
                
    print("Done")

    

def mainMenu():    
    print("\nMain Menu")
    print("--------------------")
    print("1. Display Existing Projects")
    print("2. Create a new Project")
    print("3. Post images")
    print("5. Exit")


mainMenu()
menuOption = int(input("Select a menu Option "))

print(menuOption)

while menuOption != 5:
    
    if menuOption == 1:
        displayExistingProjects()
    elif menuOption == 2:
        addNewProject()
    elif menuOption == 3:
        postImages()
    elif menuOption == 5:
        exit()

    mainMenu()
    menuOption = int(input("Select a menu Option "))
        
