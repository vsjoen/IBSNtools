import csv
from PIL import Image
from pathlib import Path
import glob, os, sys
import piexif

row = (1, 2, 3)

#initDir = './imageFolder/'
#saveTo = './data_exported.csv'

initDir = './' + sys.argv[1] + '/'
saveTo = sys.argv[2]

ogImages = glob.glob(initDir + '/*/*/*.*')
exportList = []
headers = ['filename', 'width', 'height', 'filesize']
exifNone = {'0th': {}, 'Exif': {}, 'GPS': {}, 'Interop': {}, '1st': {}, 'thumbnail': None}

i = 0
for image in ogImages:
    imagedata_o = Image.open(image)
    name_o = os.path.basename(image)
    width_o, height_o = imagedata_o.size
    file_stats_o = os.stat(image)
    size_o = file_stats_o.st_size
    quantize_o = imagedata_o.quantization
    qtable_o = quantize_o
    exif_o = piexif.load(image)

    socialNet = glob.glob(os.path.dirname(image) + '/*/*.*')
    exportList.append([name_o, width_o, height_o, size_o])

    j = 0
    for image2 in socialNet:
        imagedata_m = Image.open(image2)
        name_m = os.path.basename(image2)
        network_m = os.path.basename(os.path.dirname(image2))
        width_m, height_m = imagedata_m.size
        file_stats_m = os.stat(image2)
        size_m = file_stats_m.st_size
        quantize_m = imagedata_m.quantization
        qtable_m = quantize_m
        exif_m = piexif.load(image2)
        if name_o == name_m:
            renamed = 0
        else:
            renamed = 1
        if width_o == width_m and height_o == height_m:
            resized = 0
        else:
            resized = 1
        if quantize_o == quantize_m:
            recompressed = 0
        else:
            recompressed = 1
        if exif_o == exifNone:
            reexif = 'No EXIF'
        else:
            if exif_m == exifNone:
                reexif = 'Deleted'
            else:
                if exif_m == exif_o:
                    reexif = 'Identical'
                else:
                    reexif = 'Edited'
        if i == 0:
            headers.append(network_m + ' renamed')
            headers.append(network_m + ' resized')
            headers.append(network_m + ' recompressed')
            headers.append(network_m + ' exif')
        exportList[i].append(renamed)
        exportList[i].append(resized)
        exportList[i].append(recompressed)
        exportList[i].append(reexif)
        j = j + 1
    i = i + 1

# open the file in the write mode
f = open(saveTo, 'w')

# create the csv writer
writer = csv.writer(f)

# write a row to the csv file
writer.writerow(headers)
writer.writerows(exportList)

# close the file
f.close()
