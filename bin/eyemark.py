"""
Author: Karun Kannan
Last Update: 1/3/18
"""

import cv2
import numpy as np
import glob
import xlwt
from api import select_and_compute
from matplotlib import pyplot as plt

book = xlwt.Workbook()
sheet = book.add_sheet("Results")
sheet.write(0, 0, "Image Name")
sheet.write(0, 1, "AA")
sheet.write(0, 2, "Max Thickness")
sheet.write(0, 3, "ACRC")
sheet.write(0, 4, "PCRC")
sheet.write(0, 5, "Depth of AC")
sheet.write(0, 6, "Flag")

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
        fname = img[i]
        valid, AA, max_thickness, ACRC, PCRC, depth = select_and_compute(fname)
        if valid == False:
            i = i - 1
        else:
            sheet.write(i+1, 0, fname)
            sheet.write(i+1, 1, AA)
            sheet.write(i+1, 2, max_thickness)
            sheet.write(i+1, 3, ACRC)
            sheet.write(i+1, 4, PCRC)
            sheet.write(i+1, 5, depth)
            sheet.write(i+1, 6, "N/A")

book.save("Results.xls")

