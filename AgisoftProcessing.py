import os
import json
import urllib.request
import requests
import shutil # Need Install posibly
import PhotoScan
import time
from time import sleep

# Web Server URL
web_server = "http://localhost:8000"

MonitorDirectory = "c:\\monitor\\"


def process(project_id, name):

    doc = PhotoScan.app.document

    chunk=doc.addChunk()
    chunk.label=name

    #Setting variables
    KEYPOINT = 40000
    TEXTURE_SIZE = 4096
    
    images = urllib.request.urlopen(web_server + "/selfie/v1/projects/" + str(project_id) + "/images")
    images_json_format = json.loads(images.read().decode())

    # Get Images from here
    photo_path = 'C:\\Users\\tobal\\Desktop\\Scanner\\img\\' + name + '\\'

    # Get Images from here
    mask_path = 'C:\\Users\\tobal\\Desktop\\Scanner\\mk\\' + name + '\\'

    #export file using this path
    export_to = 'C:\\Users\\tobal\\Desktop\\Scanner\\save\\' + name + '.3ds'

    #Project save path
    project_path = 'C:\\Users\\tobal\\Desktop\\Scanner\\export\\' + name + '.psz'

    if os.path.exists(photo_path):
        log("Removing " + photo_path)    
        shutil.rmtree(photo_path)

    os.mkdir(photo_path)
	
    if os.path.exists(mask_path):
        log("Removing " + mask_path)
        shutil.rmtree(mask_path)

    os.mkdir(mask_path)

    i = 1
    for img in images_json_format:
        log("Retrieving " + web_server + "/" + img['url'] + '------- ' + img['type'])

        if img['type'] == 'masking_image':
            urllib.request.urlretrieve( web_server + "/" + img['url'].replace('\\', '/'), mask_path + str(i) + '.jpg')
            mask_path = mask_path + str(i) + '.jpg'
            
        elif img['type'] == 'processing_image':
            urllib.request.urlretrieve( web_server + "/" + img['url'].replace('\\', '/'), photo_path + str(i) + ".jpg")

        i = i + 1

    log(str(i) + " Images has been added")

    update_queue =requests.put(web_server + '/selfie/v1/photoscan_queues/update/' + str(project_id), data = {'status': 'processed'})

    #Get image path as list
    image_list = os.listdir(photo_path)
    path_list = list()

    for image in image_list:
        if "jpg" in image.lower():
            path_list.append(photo_path + image)
        else:
            log("No photos are in this folder")

    #Print the photos in the list with their file path
    print(path_list)


    #Add photos to the chunk
    chunk.addPhotos(path_list)

    
    #Marker Detection
    #Detect Markers
    log("---Detecting Markers---")
    chunk.detectMarkers(PhotoScan.TargetType.CircularTarget12bit, 60)
    
    #Setting distance between the markers
    #Numbers in chunk.markers[#] are relative to the markers list in the workspace
    #The index list starts at 0, distance = '' is in metres.
    print ("Adding the Scale Bars")
    ab = chunk.addScalebar(chunk.markers[0], chunk.markers[1])
    ab.reference.distance = 0.10
    bc = chunk.addScalebar(chunk.markers[1], chunk.markers[2])
    bc.reference.distance = 0.10
    cd = chunk.addScalebar(chunk.markers[2], chunk.markers[3])
    cd.reference.distance = 0.10
    de = chunk.addScalebar(chunk.markers[3], chunk.markers[4])
    de.reference.distance = 0.10
    ae = chunk.addScalebar(chunk.markers[0], chunk.markers[4])
    ae.reference.distance = 0.10
    
    #Setting the location of the markers ((X,Y,Z)) values in metres
    #Without this there wont be a pentagon shape
    log("Setting the location of the markers")
    chunk.markers[0].reference.location = PhotoScan.Vector((0,0,0.3))
    chunk.markers[1].reference.location = PhotoScan.Vector((0.3,0,0))
    chunk.markers[2].reference.location = PhotoScan.Vector((0,0,-0.3))
    chunk.markers[3].reference.location = PhotoScan.Vector((-0.3,0,0))
    chunk.markers[4].reference.location = PhotoScan.Vector((0,0,0))
    
    #Update user interface during long operations
    PhotoScan.app.update()
    
    #Auto-masking the photo, being applied to all images/cameras when calling the path.
    #Set tolerance higher to get better masking results
    log("Creating auto mask")
    chunk.importMasks(path=mask_path, source=PhotoScan.MaskSourceBackground, operation=PhotoScan.MaskOperationReplacement, tolerance=100)
    
    #Update user interface during long operations
    PhotoScan.app.update()

    #Align the Images, Integers required as arguments if we do not use PhotoScan class
    chunk.matchPhotos(accuracy=PhotoScan.MediumAccuracy, preselection=PhotoScan.GenericPreselection, filter_mask=False, keypoint_limit=KEYPOINT)

    chunk.alignCameras()

    chunk.buildDenseCloud(quality=PhotoScan.MediumQuality)
    chunk.buildModel(surface=PhotoScan.Arbitrary, interpolation=PhotoScan.EnabledInterpolation)
    chunk.buildUV(mapping=PhotoScan.GenericMapping)
    chunk.buildTexture(blending=PhotoScan.MosaicBlending, size=TEXTURE_SIZE)

    doc.save(project_path)


    #EXPORT HERE
    chunk.exportModel(export_to, binary=False, precision=6, texture_format=PhotoScan.ImageFormatJPEG, texture=True, normals=True, colors=True, cameras=False, format=PhotoScan.ModelFormat3DS)

    log("Processing of Script is now complete")


projects = urllib.request.urlopen(web_server + "/selfie/v1/photoscan_queues")
data = json.loads(projects.read().decode())

def log(msg):
    print (msg)
    logfile = open(MonitorDirectory + "Process_log.txt", "a")
    logfile.write(time.strftime("%H:%M:%S ") + msg + "\n")
    logfile.close()
    

log("Starting automatic processing engine")
PhotoScan.app.update()

while (True):
    log("Checking for new tasks..")
    sleep(2)

    projects = urllib.request.urlopen(web_server + "/selfie/v1/photoscan_queues")
    data = json.loads(projects.read().decode())

    log(str(len(data)) +  " is here")

    i = 0

    if len(data) > 0:
        log("Some projects has been found")
		
        for project in data:
            log(project['name'] + ": Project is being retrieved")
            process(project['id'], project['name'])
            i = i + 1
