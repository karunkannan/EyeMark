"""
Author: Karun Kannan
Last Update: 1/3/18
"""

import cv2
import numpy as np
import glob
import pickle
from api import select_and_compute
from matplotlib import pyplot as plt

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
        valid, AA, max_thickness, ACRC, PCRC = select_and_compute(fname)
        if valid == False:
            i = i - 1
        else:
            print("WE WRITING FAM")


