"""
Author: Karun Kannan
Last Update: 12/21/17
"""

import cv2
import numpy as np
import glob
import time
from matplotlib import pyplot as plt

points = []

#mouse click event logs all points into lis
#TODO: Allow users to go back and fix points without redoing the image
def get_val(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        points.append((x,y))

#calculate distance between two points
def distance(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    x = np.power((x1-x1), 2)
    y = np.power((y1-y2), 2)
    return np.sqrt(x + y)

while(1):
    #get directory information
    img_dir = input("Enter Folder with Images, enter quit if done: ")
    img_dir = img_dir.strip()
    #break when user quits
    if img_dir == 'quit': break
    img_dir = img_dir + "/*"

    #gather files
    #try:
    img = glob.glob(img_dir)
    #except IOError:
    #    print("Invalid image folder, try again.")
    #    continue
    plt.show()
    plt.close()

    #open up designated window display
    cv2.namedWindow("Image Displayer")
    cv2.setMouseCallback("Image Displayer", get_val)

    #loop and process
    for i in img:
        us_img = cv2.imread(i)
        cv2.imshow("Image Displayer", us_img)

        #only breaks out of wait sequence once esc key is clicked
        k = cv2.waitKey(0) & 0xFF
        if k == 27:
            dist = np.float32(input("What is the control distance?:"))
            normalize = np.divide(dist, distance(points[0], points[1]))

            #draw AA line
            cv2.line(us_img, points[2], points[3], (255,0,0), 5)
            #compute AA line length
            AA = distance(points[2], points[3])*normalize
            print("AA distance is %d mm" % AA)

            #show image
            cv.imshow(i, us_img)
            #clear points for next
            #TODO: Allow users to restart image
            points = []
            continue
