import os
import json
import urllib.request
import shutil # Need Install posibly
import PhotoScan

# Web Server URL
web_server = "http://localhost:8000"


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

    #export file using this path
    export_to = 'C:\\Users\\tobal\\Desktop\\Scanner\\save\\' + name + '.3ds'

    #Project save path
    project_path = 'C:\\Users\\tobal\\Desktop\\Scanner\\export\\' + name + '.psx'

    if os.path.exists(photo_path):
        print("Removing " + photo_path)    
        shutil.rmtree(photo_path)

    os.mkdir(photo_path)

    i = 1
    for img in images_json_format:
        print("Retrieving " + web_server + "/" + img['url'])
        urllib.request.urlretrieve( web_server + "/" + img['url'].replace('\\', '/'), photo_path + str(i) + ".jpg")
        i = i + 1

    print(str(i) + " Images has been added")

    #Get image path as list
    image_list = os.listdir(photo_path)
    path_list = list()

    for image in image_list:
        if "jpg" in image.lower():
            path_list.append(photo_path + image)
        else:
            print("No photos are in this folder")

    #Print the photos in the list with their file path
    print(path_list)


    #Add photos to the chunk
    chunk.addPhotos(path_list)

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

    print("Processing of Script is now complete")


projects = urllib.request.urlopen(web_server + "/selfie/v1/photoscan_queues")
data = json.loads(projects.read().decode())

i = 0
for project in data:
    print(project['name'] + ": Project is being retrieved")
    #urllib.request.urlretrieve( web_server + "/" + project['url'], photo_path + str(i) + ".jpg")
    process(project['id'], project['name'])
    i = i + 1
