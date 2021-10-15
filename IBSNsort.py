import cv2
import glob
import numpy as np
from shutil import copyfile
import os
import sys

width = 500
height = 300
dim = (width, height)


folderArg = './' + sys.argv[1] + '/'
socialNets = glob.glob(folderArg + 'unsorted/*/')

for folder in socialNets:
    downList = glob.glob(folder + '/*.jpg')
    ogList = glob.glob(folderArg + 'sorted/*/*/*.*')
    socialName = os.path.basename(os.path.dirname(folder))

    def similarity(image1, image2):
        img = cv2.imread(image1)
        if img is None:
            sys.exit('Could not read the image.')

        img2 = cv2.imread(image2)
        if img2 is None:
            sys.exit('Could not read the image.')

        resized = cv2.resize(img2, dim, interpolation = cv2.INTER_AREA)
        og_resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

        original = og_resized
        image_to_compare = resized

        sift = cv2.SIFT_create()
        kp_1, desc_1 = sift.detectAndCompute(original, None)
        kp_2, desc_2 = sift.detectAndCompute(image_to_compare, None)

        index_params = dict(algorithm=0, trees=5)
        search_params = dict()
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(desc_1, desc_2, k=2)

        good_points = []
        for m, n in matches:
            if m.distance < 0.6*n.distance:
                good_points.append(m)

        # Define how similar they are
        number_keypoints = 0
        if len(kp_1) <= len(kp_2):
            number_keypoints = len(kp_1)
        else:
            number_keypoints = len(kp_2)

        return (len(good_points) / number_keypoints * 100)
    for i in ogList:
        print(i)
        for j in downList:
            sim = similarity(i, j)
            if sim > 50:
                print(j)
                print(sim)
                copyFile = os.path.dirname(i) + '/' + socialName + '/' + os.path.basename(j)
                copyFolder = os.path.dirname(i) + '/' + socialName
                isExist = os.path.exists(copyFolder)
                if not isExist:
                    os.makedirs(copyFolder)
                    print(socialName + " folder created")
                    copyfile(j, copyFile)
                    print("file copied" + '\n')
                else:
                    copyfile(j, copyFile)
                    print(socialName + " folder exists")
                    print("file copied" + '\n')
