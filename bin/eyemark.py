"""
Author: Karun Kannan
Last Update: 12/24/17
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
        cv2.circle(us_img, (x,y), 10, (0,255,0))
        cv2.imshow("Image Displayer", us_img)

#calculate distance between two points
def distance(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    x = np.power((x1-x2), 2)
    y = np.power((y1-y2), 2)
    return np.sqrt(x + y)

#find center and point to draw line too
def calc_center(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    #calc the center
    c_x = (x2 + x1)/2
    c_y = (y2 + y1)/2
    #calc perp point, defined as v
    mag = distance((c_x, c_y), pt2)
    v_x = (y2 - c_y)/mag
    v_y = (c_x - x2)/mag
    v_x = c_x + 100*v_x
    v_y = c_y + 100*v_y
    v = (int(v_x), int(v_y))
    c_val = (int(c_x), int(c_y))
    return c_val, v

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
    cv2.namedWindow("Image Displayer", cv2.WINDOW_KEEPRATIO)
    cv2.setMouseCallback("Image Displayer", get_val)

    #loop and process
    for i in img:
        us_img = cv2.imread(i)
        cv2.imshow("Image Displayer", us_img)

        #only breaks out of wait sequence once esc key is clicked
        k = cv2.waitKey(0) & 0xFF
        if k == 27:
            dist = np.float32(input("What is the control distance?:"))
            normalize = np.divide(np.float32(dist),
                    np.float32(distance(points[0], points[1])))

            #draw AA line
            cv2.line(us_img, points[2], points[3], (255,0,0), 1)
            #compute AA line length
            AA = np.float32(distance(points[2], points[3]))*normalize
            print("AA distance is %.2f mm" % AA)

            #draw central line
            #TODO: Deal with cutoff images, idea: slide center point once drawn
            c, perp_point = calc_center(points[2], points[3])
            cv2.line(us_img, c, perp_point, (255,0,0), 1)

            #draw inner ellipse
            vertical_radius = int(distance(c, points[4]))
            horizontal_radius = int(distance(points[3], points[2])/2)
            cv2.ellipse(us_img, c, (horizontal_radius, vertical_radius), 0, 180
                    ,360, (255,0,0), 1)

            #show image
            cv2.imshow(i, us_img)
            #clear points for next
            #TODO: Allow users to restart image
            points = []
            continue

