"""
Author: Karun Kannan
Last Update: 12/21/17
"""

import cv2
import numpy as np
import glob
from matplotlib import pyplot as plt

cont = True #variable to keep looping
while(cont):
    #get directory information
    img_dir = input("Enter Folder with Images, enter quit if done: ")
    img_dir = img_dir.strip()
    #break when user quits
    if img_dir == 'quit': break
    img_dir = img_dir + "/*"

    #gather files
    img = glob.glob(img_dir)

    #loop and process
    for i in img:
        us_img = cv2.imread(i)
        plt.imshow(us_img)
        plt.show()
        break

