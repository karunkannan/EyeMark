"""
Author: Karun Kannan
Last Update: 3/24/18
"""

import cv2
import numpy as np
import glob
import xlwt
from api import select_and_compute
from matplotlib import pyplot as plt

def abnormality_check(test, typ, threshold):
    if (test > typ*(threshold + 1)) or (test < typ*(1 - threshold)):
        return 1
    else:
        return 0


book = xlwt.Workbook()
sheet = book.add_sheet("Results")
sheet.write(0, 0, "Image Name")
sheet.write(0, 1, "AA")
sheet.write(0, 2, "Max Thickness")
sheet.write(0, 3, "ACRC")
sheet.write(0, 4, "PCRC")
sheet.write(0, 5, "Depth of AC")
sheet.write(0, 6, "Flag")
"""
AA_typ = float(input("Typical AA length (mm): "))
max_thickness_typ = float(input("Typical Max. Thickness (mm): "))
ACRC_typ = float(input("Typical radius of ACRC (mm): "))
PCRC_typ = float(input("Typical radius of PCRC (mm): "))
depth_typ = float(input("Typical depth of Anterior Chamber (mm): "))
thresh = float(input("Threshold for flagging (decimal value): "))
"""
print("Instructions:\nDouble Click to select points as specified on wiki.\nq - complete selection for given image.\nd - deletes the last selected point. \nr - resets all points for given image.\ne - exits the current image.")
print(cv2)

while(1):
    #get directory information
    img_dir = input("Enter Folder with Images, enter quit if done: ")
    img_dir = img_dir.strip()
    #break when user quits
    if img_dir == 'quit': break
    img_dir = img_dir + "/*"

    #gather files
    img = glob.glob(img_dir)

    plt.show()
    plt.close()

    #loop and process
    for i in range(len(img)):
        valid = False
        while not valid:
            fname = img[i]
            valid, AA, max_thickness, ACRC, PCRC, depth = select_and_compute(fname)
        if valid and AA == None:
            continue
        #check for flagging
        flag = ""
        if(abnormality_check(AA, AA_typ, thresh)):
            flag += "AA, "

        if(abnormality_check(max_thickness, max_thickness_typ, thresh)):
            flag += "thickness, "

        if(abnormality_check(ACRC, ACRC_typ, thresh)):
            flag += "ACRC, "

        if(abnormality_check(PCRC, PCRC_typ, thresh)):
            flag += "PCRC, "

        if(abnormality_check(depth, depth_typ, thresh)):
            flag += "depth"

        sheet.write(i+1, 0, fname)
        sheet.write(i+1, 1, AA)
        sheet.write(i+1, 2, max_thickness)
        sheet.write(i+1, 3, ACRC)
        sheet.write(i+1, 4, PCRC)
        sheet.write(i+1, 5, depth)
        sheet.write(i+1, 6, flag)
        book.save("Results.xls")

        plt.show()
        plt.close()

book.save("Results.xls")

