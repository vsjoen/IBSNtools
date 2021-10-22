import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from PIL import ImageTk, Image, ExifTags
from PIL.ExifTags import TAGS
from pathlib import Path
import glob, os, sys
import ntpath
import math
import re
import fnmatch
import piexif
from functools import partial

# global variables
pic = None
fname = None
fpath = None
fcam = None
fsize = None
iwidth = None
iheight = None
exifd = None
qtable_o = []
selected_image = None
img2 = None
image2 = None
g_fontsize = 10
m_fontsize = g_fontsize
g_font = 'Helvetica'
biglist = []
button_identities = []
allImages = []
selImage = 0
selselImage = ''
hueOffset = 160
exifNone = {'0th': {}, 'Exif': {}, 'GPS': {}, 'Interop': {}, '1st': {}}
folderBool = 0
hasQuantize = 0

# create the root window
root = tk.Tk()
root.title('IBSNview - Image Ballistics in Social Networks')
root.resizable(False, False)
#root.geometry('1200x800')
#root.eval('tk::PlaceWindow . center')
#frame = Frame()
mainFrameLeft = Frame()
mainFrameRight = Frame()
mainFrameQt = Frame(mainFrameLeft)
qtFrame1 = Frame(mainFrameQt)
qtFrame2 = Frame(mainFrameQt)
buttonFrame = Frame(mainFrameLeft)

def hsv2rgb(h, s, v):

    """HSV to RGB

    :param float h: 0.0 - 360.0
    :param float s: 0.0 - 1.0
    :param float v: 0.0 - 1.0
    :return: rgb
    :rtype: list

    """

    c = v * s
    x = c * (1 - abs(((h/60.0) % 2) - 1))
    m = v - c

    if 0.0 <= h < 60:
        rgb = (c, x, 0)
    elif 0.0 <= h < 120:
        rgb = (x, c, 0)
    elif 0.0 <= h < 180:
        rgb = (0, c, x)
    elif 0.0 <= h < 240:
        rgb = (0, x, c)
    elif 0.0 <= h < 300:
        rgb = (x, 0, c)
    elif 0.0 <= h < 360:
        rgb = (c, 0, x)

    return list(map(lambda n: (n + m) * 255, rgb))

def align(word, number):
    return '{:<10s}{:>10d}'.format(word, number)

def select_folder():
    global folderBool
    folderBool = 1
    select_file()

def select_file():
    global selected_image
    global selImage
    global folderBool
    filetypes = [('Image files', '.jpeg .jpg .png .tif .tiff')]

    if folderBool == 1:
        folder = fd.askdirectory(
            initialdir = './',
             title="Choose folder")
        allFiles = glob.glob(folder + '/*/*/*.*')
        filename = allFiles[0]
        folderBool = 0
    else:
        filename = fd.askopenfilename(
        title ='Open Image',
        initialdir ='./',
        filetypes = filetypes)

    select_file.var = filename
    if hasattr(select_file, 'var'):
        selected_image = select_file.var
        n = 0
        for i in allImages:
            path1 = Path(selected_image)
            path2 = Path(i)
            if path_leaf(selected_image) == path_leaf(i) and \
            path1.parent.absolute().parent.absolute() == \
            path2.parent.absolute().parent.absolute() :
                selImage = n
            n = n + 1
        load_image()
        load_data()

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def quick_file():
    global selected_image
    selected_image = './test/Nikon D90/r000da54ft/r000da54ft.tif'
    #selected_image = './imageFolder/CANON_650D_720X480_INDOOR/IMG_2635/IMG_2635.JPG'
    load_image()
    load_data()

def donothing():
    print('Nothing')

def next_file():
    global selImage
    global selected_image
    if selImage >= 3:
        selImage = 0
    else:
        selImage = selImage + 1
    selected_image = allImages[selImage]
    load_image()
    load_data()

def prev_file():
    global selImage
    global selected_image
    if selImage <= 0:
        selImage = len(allImages)-1
    else:
        selImage = selImage - 1
    selected_image = allImages[selImage]
    load_image()
    load_data()

def preferences():
    prefWin = Toplevel(root)
    prefWin.title('IBSNview - Preferences')
    #g_fontsize = 14
    # variable = Var(prefWin)
    # w = OptionMenu(prefWin, g_fontsize, 12, 14, 16)
    # w.pack()

def exif():
    exifwin = Toplevel(root)
    exifwin.title(f'{fname} - EXIF Data')
    exifText = tk.Text(exifwin, height = 140)
    for x in exifList:
        exifText.insert(END, x + '\n')
    exifText.grid()

def exifmore(selected):
    exifList2 = []
    exif_dict2 = biglist[selected][6]

    if 'thumbnail' in exif_dict2:
        del exif_dict2['thumbnail']

    for ifd in exif_dict2:
        #print(f'{ifd}:')
        exifList2.append(f'{ifd}:')
        for tag in exif_dict2[ifd]:
            tag_name = piexif.TAGS[ifd][tag]["name"]
            tag_value = exif_dict2[ifd][tag]
            # Avoid print a large value, just to be pretty
            if isinstance(tag_value, bytes):
                tag_value = tag_value[:10]
            #print(f'\t{tag_name:25}: {tag_value}')
            exifList2.append(f'\t{tag_name:25}: {tag_value}')
    exifmore = Toplevel(root)
    exifmore.title(f'{ntpath.basename(selected_image)} - {biglist[selected][0]} EXIF Data')
    exifText = tk.Text(exifmore, height = 140)
    for x in exifList2:
        exifText.insert(END, x + '\n')
    exifText.grid()

# show more info
def more(selected):
    inforows = 4
    morewin = Toplevel(root)
    morewin.resizable(False, False)
    infoFrame = Frame(morewin)
    dataFrame = Frame(morewin)
    qt1Frame = Frame(morewin)
    qt2Frame = Frame(morewin)
    subTopLeft = Frame(morewin)
    subTopRight = Frame(morewin)
    subLeft = Frame(morewin)
    subRight = Frame(morewin)
    morewin.title(f'{ntpath.basename(selected_image)} - {biglist[selected][0]}')

    tk.Label(subTopLeft, text = f'File Name:').grid(column = 0, row = 0, sticky = W)
    tk.Label(subTopRight, text = f'{biglist[selected][1]}').grid(column = 1, row = 0, sticky = E)

    tk.Label(subTopLeft, text = f'File Size:').grid(column = 0, row = 1, sticky = W)
    tk.Label(subTopRight, text = f'{biglist[selected][2]}').grid(column = 1, row = 1, sticky = E)

    tk.Label(subTopLeft, text = f'Image Width:').grid(column = 0, row = 2, sticky = W)
    tk.Label(subTopRight, text = f'{biglist[selected][3]} px').grid(column = 1, row = 2, sticky = E)

    tk.Label(subTopLeft, text = f'Image Height:').grid(column = 0, row = 3, sticky = W)
    tk.Label(subTopRight, text = f'{biglist[selected][4]} px').grid(column = 1, row = 3, sticky = E)

    qt1 = biglist[selected][5][0]
    qt2 = biglist[selected][5][1]

    tk.Label(subLeft, text = f'Quantization Table 1:').grid(column = 0, row = 0, sticky = W, columnspan = 8)
    tk.Label(subRight, text = f'Quantization Table 2:').grid(column = 0, row = 0, sticky = W, columnspan = 8)
    n = 0
    for i in range(8):
        for j in range(8):
            value = qt1[n]
            hsv = hsv2rgb((hueOffset + value * 2) % 255, .5, .7)
            rcol = '#%02x%02x%02x' % (int(hsv[0]), int(hsv[1]), int(hsv[2]))
            if value < 10:
                numPad = 6
            elif value < 100:
                numPad = 3
            else:
                numPad = 0
            tk.Label(subLeft, bg = rcol, fg = "white",
            text = f'{value}').grid(sticky=(N, S, E, W), column = i, row = j + 1, padx = 1, pady = 1, ipadx = 2 + numPad, ipady = 3)
            n = n + 1

    n = 0
    for i in range(8):
        for j in range(8):
            value = qt2[n]
            hsv = hsv2rgb((hueOffset + value * 2) % 255, .5, .7)
            rcol = '#%02x%02x%02x' % (int(hsv[0]), int(hsv[1]), int(hsv[2]))
            if value < 10:
                numPad = 6
            elif value < 100:
                numPad = 3
            else:
                numPad = 0
            tk.Label(subRight, bg = rcol, fg = "white",
            text = f'{value}').grid(sticky=(N, S, E, W), column = i, row = j + 1, padx = 1, pady = 1, ipadx = 2 + numPad, ipady = 3)
            n = n + 1

    subTopLeft.grid(column = 0, row = 0, padx = 10, pady = 10, sticky = W)
    subTopRight.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = E)
    subLeft.grid(column = 0, row = 1, padx = 10, pady = 10, sticky = W)
    subRight.grid(column = 1, row = 1, padx = 10, pady = 10, sticky = W)

# canvas for image
canvas = tk.Canvas(mainFrameLeft, width = 468, height = 312)
canvas.grid(padx = (20, 20), column = 0, columnspan = 1,
row = 0, sticky = W)

button_pad = 0
btny = 7
btnx = 1
tk.Button(buttonFrame, text = 'Open Folder', command = select_folder).grid(column = 0, row = 1, padx = button_pad, ipady=btny, ipadx=btnx)
tk.Button(buttonFrame, text = 'Open Image', command = select_file).grid(column = 1, row = 1, padx = button_pad, ipady=btny, ipadx=btnx)
tk.Button(buttonFrame, text = '< Prev', command = next_file).grid(column = 2, row = 1, padx = button_pad, ipady=btny, ipadx=btnx)
tk.Button(buttonFrame, text = 'Next >', command = prev_file).grid(column = 3, row = 1, padx = button_pad, ipady=btny, ipadx=btnx)
tk.Button(buttonFrame, text = 'View Exif', command = exif).grid(column = 4, row = 1, padx = button_pad, ipady=btny, ipadx=btnx)

def load_image():
    # change image on canvas
    global img2
    global image2
    global allImages
    img2 = Image.open(selected_image)
    img2 = img2.resize((468, 312), Image.ANTIALIAS)
    image2 = ImageTk.PhotoImage(img2)
    canvas.itemconfig(image_id, image = image2)
    allImages = glob.glob('./imageFolder/*/*/*.*')

exifList = []
def load_data():
    global selected_image
    global fpath
    global fcam
    global fname
    global fsize
    global iwidth
    global iheight
    global exifd
    global mainFrameRight
    global qtable_o

    image_o = selected_image

    name_o = ntpath.basename(selected_image)

    rootdir = os.path.dirname(image_o)
    dirlist = []
    pathlist = []
    for file in os.listdir(rootdir):
        d = os.path.join(rootdir, file)
        if os.path.isdir(d):
            pathlist.append(d)
            dirlist.append(ntpath.basename(d))

    # read the image data using PIL
    imagedata_o = Image.open(image_o)

    # extract EXIF data
    exif_dict = piexif.load(selected_image)
    #print(exif_dict)
    #exifdata_o = imagedata_o.getexif()

    # iterating over all EXIF data fields
    global exifList
    exifList.clear()

    if 'thumbnail' in exif_dict:
        del exif_dict['thumbnail']

    exifdata_o = exif_dict

    for ifd in exif_dict:
        #print(f'{ifd}:')
        exifList.append(f'{ifd}:')
        for tag in exif_dict[ifd]:
            tag_name = piexif.TAGS[ifd][tag]["name"]
            tag_value = exif_dict[ifd][tag]
            # Avoid print a large value, just to be pretty
            if isinstance(tag_value, bytes):
                tag_value = tag_value[:10]
            #print(f'\t{tag_name:25}: {tag_value}')
            exifList.append(f'\t{tag_name:25}: {tag_value}')

    file_stats_o = os.stat(image_o)

    if hasattr(imagedata_o, 'quantization'):
        quantize_o = imagedata_o.quantization
        qtable_o = quantize_o
        hasQuantize = 1
    else:
        hasQuantize = 0

    width_o, height_o = imagedata_o.size

    fpath = image_o
    cam_o = os.path.basename(os.path.dirname(os.path.dirname(fpath)))
    fcam = cam_o
    fname = name_o
    fsize = file_stats_o.st_size
    iwidth = width_o
    iheight = height_o
    exifd = exifdata_o

    fpath_sv.set(f'File Path: {fpath}')

    fcam_sv.set(f'Camera: {fcam}')

    fname_sv.set(f'File Name: {fname}')

    if file_stats_o.st_size > 1000000:
        fsize_sv.set(f'File Size: {round(fsize / (1024 * 1024), 2)} MB')
    else:
        fsize_sv.set(f'File Size: {round(fsize / 1024, 2)} KB')

    fdim_sv.set(f'Image Size: {iwidth}x{iheight} px')

    exifd_sv.set(f'EXIF Data: {exifd}')

    if exifdata_o == exifNone:
        exifd_sv.set(f'EXIF Data: No')
    else:
        exifd_sv.set(f'EXIF Data: Yes')

    if qtable_o != []:
        for widget in qtFrame1.winfo_children():
                widget.destroy()

        for widget in qtFrame2.winfo_children():
                widget.destroy()

        tk.Label(qtFrame1, text = f'Quantization Table 1:').grid(column = 0,
        row = 0, sticky = W, columnspan = 8)
        tk.Label(qtFrame2, text = f'Quantization Table 2:').grid(column = 0,
        row = 0, sticky = W, columnspan = 8)
        n = 0
        for i in range(8):
            for j in range(8):
                value = qtable_o[0][n]
                hsv = hsv2rgb((hueOffset + value * 2) % 255, .5, .7)
                rcol = '#%02x%02x%02x' % (int(hsv[0]), int(hsv[1]), int(hsv[2]))
                if value < 10:
                    numPad = 6
                elif value < 100:
                    numPad = 3
                else:
                    numPad = 0
                tk.Label(qtFrame1, bg = rcol, fg = "white",
                text = f'{value}').grid(sticky=(N, S, E, W), column = i, row = j + 1, padx = 1, pady = 1, ipadx = 2 + numPad, ipady = 3)
                n = n + 1

        n = 0
        for i in range(8):
            for j in range(8):
                value = qtable_o[1][n]
                hsv = hsv2rgb((hueOffset + value * 2) % 255, .5, .7)
                rcol = '#%02x%02x%02x' % (int(hsv[0]), int(hsv[1]), int(hsv[2]))
                if value < 10:
                    numPad = 6
                elif value < 100:
                    numPad = 3
                else:
                    numPad = 0
                tk.Label(qtFrame2, bg = rcol, fg = "white",
                text = f'{value}').grid(sticky=(N, S, E, W), column = i, row = j + 1, padx = 1, pady = 1, ipadx = 2 + numPad, ipady = 3)
                n = n + 1

        for widget in mainFrameRight.winfo_children():
            widget.destroy()

    # load modified
    image_m = []
    imagedata_m = []
    name_m = []
    global biglist

    rows, cols = (len(dirlist), 1)
    biglist = [[0 for i in range(cols)] for j in range(rows)]

    for i in range(len(dirlist)):
        image_m.append(glob.glob(pathlist[i] + '/*'))

        image_m_temp = str(image_m[i])[2:-2]
        #print(image_m_temp)

        imagedata_m = Image.open(str(image_m_temp))

        exifdata_m = imagedata_m.getexif()
        exifdata_m2 = piexif.load(image_m_temp)
        del exifdata_m2['thumbnail']

        file_stats_m = os.stat(image_m_temp)

        fsize_m = file_stats_m.st_size

        quantize_m = imagedata_m.quantization

        width_m, height_m = imagedata_m.size

        name_m = ntpath.basename(image_m_temp)

        # readable size on modified images
        if file_stats_m.st_size > 1000000:
            rsize_m = f'{round(fsize_m / (1024 * 1024), 2)} MB'
        else:
            rsize_m = f'{round(fsize_m / 1024, 2)} KB'

        biglist[i][0] = dirlist[i]
        biglist[i].insert(1, name_m)
        biglist[i].insert(2, rsize_m)
        biglist[i].insert(3, width_m)
        biglist[i].insert(4, height_m)
        biglist[i].insert(5, quantize_m)
        biglist[i].insert(6, exifdata_m2)

        if 'thumbnail' in biglist[i][6]:
            del exif_dict['thumbnail']

        #check exifdata
        if exifdata_o == exifNone:
            'EXIF Data: No EXIF'
        else:
            if exifdata_m2 == exifNone:
                exiftrue = 'EXIF Data: Deleted'
            else:
                if exifdata_m2 == exifdata_o:
                    exiftrue = 'EXIF Data: Identical'
                else:
                    exiftrue = 'EXIF Data: Edited'

        # check re-name
        if name_m == name_o:
            renamed = 'Re-Named: No'
        else:
            renamed = 'Re-Named: Yes'

        # check re-size
        if width_o == width_m and height_o == height_m:
            resized = 'Re-Sized: No'
        else:
            resized = 'Re-Sized: Yes'

        # check re-compress
        if hasQuantize == 1:
            if quantize_m == quantize_o:
                recompressed = 'Re-Compressed: No'
            else:
                recompressed = 'Re-Compressed: Yes'
        else:
            recompressed = 'Re-Compressed: Yes'

        lines = 8
        newcol = 4
        mod_padx = (10, 30)
        gridcol = 2
        gridcols = math.floor(i/newcol)

        tk.Label(mainFrameRight,
        text = dirlist[i]).grid(pady = (0, 2), sticky = W, column = gridcols,
        padx = mod_padx, row = (0 + (lines * i)) % (lines * newcol))

        ttk.Separator(mainFrameRight, orient='horizontal').grid(sticky = 'EW', column = gridcols,
        padx = mod_padx, row = (1 + (lines * i)) % (lines * newcol), pady = (2, 7))

        tk.Label(mainFrameRight, text = exiftrue).grid(sticky = W, column = gridcols,
        padx = mod_padx, row = (2 + (lines * i)) % (lines * newcol))

        tk.Label(mainFrameRight, text = renamed).grid(sticky = W, column = gridcols,
        padx = mod_padx, row = (3 + (lines * i)) % (lines * newcol))

        tk.Label(mainFrameRight, text = resized).grid(sticky = W, column = gridcols,
        padx = mod_padx, row = (4 + (lines * i)) % (lines * newcol))

        tk.Label(mainFrameRight, text = recompressed).grid(sticky = W,
        column = gridcols, padx = mod_padx, row = (5 + (lines * i)) % (lines * newcol))

        button = ttk.Button(mainFrameRight, text = 'More Info',
        command = partial(more, i)).grid(pady = 5, sticky = W, column = gridcols,
        padx = mod_padx, row = (6 + (lines * i)) % (lines * newcol))

        button = ttk.Button(mainFrameRight, text = 'View Exif',
        command = partial(exifmore, i)).grid(pady = (0, 10), sticky = W, column = gridcols,
        padx = mod_padx, row = (7 + (lines * i)) % (lines * newcol))

        button_identities.append(button)

mainFrameLeft.grid(column = 0, row = 0, sticky = 'nw', pady = 20)
mainFrameQt.grid(column = 0, row = 7, sticky = 'sw', pady = (20, 10))
qtFrame1.grid(column = 0, row = 2, padx = (20, 5))
qtFrame2.grid(column = 1, row = 2, padx = (5, 20))
mainFrameRight.grid(column = 1, row = 0, columnspan = 2, sticky = 'nw', pady = (18, 0))
buttonFrame.grid(column = 0, row = 1, padx = (20, 0), pady = (6, 15), sticky = W)

# images
img1 = Image.open('defaultimage.jpg')
image1 = ImageTk.PhotoImage(img1)

# set first image on canvas
image_id = canvas.create_image(0, 0, anchor = 'nw', image = image1)

fpath_sv = tk.StringVar()
fcam_sv = tk.StringVar()
fname_sv = tk.StringVar()
fsize_sv = tk.StringVar()
fdim_sv = tk.StringVar()
exifd_sv = tk.StringVar()
fpath_sv.set(f'File Path: {fpath}')
fcam_sv.set(f'Camera: {fcam}')
fname_sv.set(f'File Name: {fname}')
fsize_sv.set(f'File Size: {fsize} KB')
fdim_sv.set(f'Image Size: {iwidth}x{iheight} px')
exifd_sv.set(f'EXIF Data: {exifd}')

# original labels
og_gridcol = 0
og_colspan = 2
og_rowstart = 2
og_padx = (20, 0)

fcam_label = Label(mainFrameLeft, textvariable = fcam_sv).grid(column = og_gridcol,
columnspan = og_colspan, padx = og_padx, row = og_rowstart + 0, sticky = W)

fname_label = Label(mainFrameLeft, textvariable = fname_sv).grid(column = og_gridcol,
columnspan = og_colspan, padx = og_padx, row = og_rowstart + 1, sticky = W)

fsize_label = Label(mainFrameLeft, textvariable = fsize_sv).grid(column = og_gridcol,
columnspan = og_colspan, padx = og_padx, row = og_rowstart + 2, sticky = W)

iheight_label = Label(mainFrameLeft, textvariable = fdim_sv).grid(column = og_gridcol,
columnspan = og_colspan, padx = og_padx, row = og_rowstart + 3, sticky = W)

exifd_label = Label(mainFrameLeft, textvariable = exifd_sv).grid(column = og_gridcol,
columnspan = og_colspan, padx = og_padx,
row = og_rowstart + 4, sticky = W)

#quick_file()

menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label = 'Open Image', command = select_file)
filemenu.add_separator()
filemenu.add_command(label = 'Exit', command = root.quit)
menubar.add_cascade(label = 'File', menu = filemenu)

filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label = 'Preferences', command = donothing)
menubar.add_cascade(label = 'Settings', menu = filemenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label = 'Help', command = donothing)
helpmenu.add_command(label = 'About', command = donothing)
menubar.add_cascade(label = 'Help', menu = helpmenu)
root.config(menu = menubar)
root.mainloop()
