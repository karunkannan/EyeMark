"""
Author: Karun Kannan
Last Update: 1/3/18
"""

import cv2
import numpy as np
import glob
import pickle
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
    multiplier = distance((c_x, c_y), points[5])
    v_x = (y2 - c_y)/mag
    v_y = (c_x - x2)/mag
    v_x = c_x + multiplier*v_x
    v_y = c_y + multiplier*v_y
    v = (int(v_x), int(v_y))
    c_val = (int(c_x), int(c_y))
    return c_val, v

#find angle between center and AA-line
def calc_angle(pt1, pt2):
    #pt1 is center, pt2 is points[3]
    c_x, c_y = pt1
    x, y = pt2
    h = distance(pt1, pt2)
    a = distance(pt1, (x, c_y))
    alpha = np.arccos(a/h)
    alpha = 180*alpha/np.pi
    if c_y > y:
        return -1*alpha
    else:
        return alpha

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

    #open up designated window display
    cv2.namedWindow("Image Displayer", cv2.WINDOW_KEEPRATIO)
    cv2.setMouseCallback("Image Displayer", get_val)
    thickness_dict = {}
    #loop and process
    for i in img:
        us_img = cv2.imread(i)
        cv2.imshow("Image Displayer", us_img)

        #only breaks out of wait sequence once esc key is clicked
        '''
        Points array values:
        0, 1: scale points: give relation between pixels and mm
        2, 3: AA line, the horizontal line at bottom
        4: Inner vertical radius
        5: Outer vertical radius
        6: Outer base radius
        '''
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

            #calculate angle between center and edge points
            alpha = calc_angle(c, points[3])

            #draw inner ellipse
            inner_radius = int(distance(c, points[4]))
            horizontal_radius = int(distance(c, points[2]))
            cv2.ellipse(us_img, c, (horizontal_radius, inner_radius), alpha, 180
                    ,360, (255,0,0), 1)

            cv2.ellipse(us_img, c, (horizontal_radius, inner_radius), alpha, 255
                    ,295, (0,255,0), 1)

            #draw outer ellipse
            outer_radius = int(distance(c, points[5]))
            cv2.ellipse(us_img, c, (horizontal_radius, outer_radius), alpha, 180
                    ,360, (255,0,0), 1)

            cv2.ellipse(us_img, c, (horizontal_radius, outer_radius), alpha, 255
                    ,295, (0,255,0), 1)
            #get the points
            inner_points = cv2.ellipse2Poly(c, (inner_radius, horizontal_radius)
                    ,int(alpha), 165, 195, 1)
            outer_points = cv2.ellipse2Poly(c, (outer_radius, horizontal_radius)
                    ,int(alpha), 165, 195, 1)

            thickness = []
            for j in range(len(inner_points)):
                thickness_j = distance((inner_points[j][0], inner_points[j][1]),
                        (outer_points[j][0], outer_points[j][1]))
                thickness.append(thickness_j*normalize)
            print("Thickness: %.2f mm" % (thickness[15]))
            thickness_dict[i] = thickness

            #draw in 3mmT points:

            #ACRC
            x1, y1 = perp_point #from the calc center
            x2, y2 = points[6]
            x_c = x1
            y_c = int(((x2 - x1)**2 + y2**2 - y1**2)/(2*(y2 - y1)))
            radius = int(distance(points[6], (x_c,y_c)))
            cv2.circle(us_img, (x_c, y_c), radius, (0,0,255))
            r_norm = radius*normalize
            print("ACRC radius: %.2f mm" % r_norm)

            #PCRC
            x1, y1 = perp_point
            diff = int(outer_radius - inner_radius)
            y1 += diff
            x2, y2 = points[2]
            x_c = x1
            y_c = int(((x2 - x1)**2 + y2**2 - y1**2)/(2*(y2 - y1)))
            radius = int(distance(points[2], (x_c, y_c)))
            cv2.circle(us_img, (x_c, y_c), radius, (0,0,255))
            r_norm = radius*normalize
            print("PCRC Radius: %.2f mm" % r_norm)


            #show image
            cv2.imshow(i, us_img)
            #clear points for next
            #TODO: Allow users to restart image
            points = []
            continue

file_name = open('test/thickness.pkle', 'wb')
pickle.dump(thickness_dict, file_name)
file_name.close()
