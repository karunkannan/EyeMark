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
img = None
img_copy = None

''' Allows opencv to select points '''
def _get_val(event, x, y, flags, param):
    global points, img, img_copy
    if event == cv2.EVENT_LBUTTONDBLCLK:
        img_copy = img.copy()
        points.append((x,y))
        cv2.circle(img, (x,y), 5, (0,255,0))
        cv2.putText(img, str(len(points) - 1), (x,y),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.imshow("Image Displayer", img)

''' Calculates distance b/w two points
    Param: Two points of form (x,y)
    Return: Distance as float
'''
def _distance(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    x = np.power((x1-x2), 2)
    y = np.power((y1-y2), 2)
    return np.sqrt(x + y)

''' Calculates the center between two points
    Param: two points of form (x,y)
    Return: two points, the center point, as well a perpendicular point
'''
def _calc_center(pt1, pt2):
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

''' Calculates the angle b/w two points
    Param: Two points of form (x,y)
    Return: Angle between them, float
'''
def _calc_angle(pt1, pt2):
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

def select_and_compute(fname):
    global img, img_copy, points
    AA = None
    max_thickness = None
    ACRC = None
    PCRC = None

    #open up designated window display
    cv2.namedWindow("Image Displayer", cv2.WINDOW_KEEPRATIO)
    cv2.setMouseCallback("Image Displayer", _get_val)
    img = cv2.imread(fname)
    img_copy = img.copy()
    while True:
        cv2.imshow("Image Displayer", img)

        '''
        Points array values:
        0, 1: scale points: give relation between pixels and mm
        2, 3: AA line, the horizontal line at bottom
        4: Inner vertical radius
        5: Outer vertical radius
        6: Outer base radius
        '''
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            if len(points) == 7:
                dist = np.float32(input('What is the control distance of this image?'))
                normalize = np.divide(np.float32(dist),
                    np.float32(_distance(points[0], points[1])))

                #draw AA line
                cv2.line(img, points[2], points[3], (255,0,0), 1)
                #compute AA line length
                AA = np.float32(_distance(points[2], points[3]))*normalize
                print("AA distance is %.2f mm" % AA)

                #draw central line
                #TODO: Deal with cutoff images, idea: slide center point once drawn
                c, perp_point = _calc_center(points[2], points[3])
                cv2.line(img, c, perp_point, (255,0,0), 1)

                #calculate angle between center and edge points
                alpha = _calc_angle(c, points[3])

                #draw inner ellipse
                inner_radius = int(_distance(c, points[4]))
                horizontal_radius = int(_distance(c, points[2]))
                cv2.ellipse(img, c, (horizontal_radius, inner_radius), alpha, 180
                        ,360, (255,0,0), 1)

                cv2.ellipse(img, c, (horizontal_radius, inner_radius), alpha, 255
                        ,295, (0,255,0), 1)

                #draw outer ellipse
                outer_radius = int(_distance(c, points[5]))
                cv2.ellipse(img, c, (horizontal_radius, outer_radius), alpha, 180
                        ,360, (255,0,0), 1)

                cv2.ellipse(img, c, (horizontal_radius, outer_radius), alpha, 255
                    ,295, (0,255,0), 1)
                #get the points
                inner_points = cv2.ellipse2Poly(c, (inner_radius, horizontal_radius)
                    ,int(alpha), 165, 195, 1)
                outer_points = cv2.ellipse2Poly(c, (outer_radius, horizontal_radius)
                    ,int(alpha), 165, 195, 1)

                thickness = []
                for j in range(len(inner_points)):
                    thickness_j = _distance((inner_points[j][0], inner_points[j][1])
                        ,(outer_points[j][0], outer_points[j][1]))
                    thickness.append(thickness_j*normalize)
                print("Thickness: %.2f mm" % (thickness[15]))
                max_thickness = thickness[15]

                #draw in 3mmT points:

                #ACRC
                x1, y1 = perp_point #from the calc center
                x2, y2 = points[6]
                x_c = x1
                y_c = int(((x2 - x1)**2 + y2**2 - y1**2)/(2*(y2 - y1)))
                radius = int(_distance(points[6], (x_c,y_c)))
                cv2.circle(img, (x_c, y_c), radius, (0,0,255))
                r_norm = radius*normalize
                ACRC = r_norm
                print("ACRC radius: %.2f mm" % r_norm)

                #PCRC
                x1, y1 = perp_point
                diff = int(outer_radius - inner_radius)
                y1 += diff
                x2, y2 = points[2]
                x_c = x1
                y_c = int(((x2 - x1)**2 + y2**2 - y1**2)/(2*(y2 - y1)))
                radius = int(_distance(points[2], (x_c, y_c)))
                cv2.circle(img, (x_c, y_c), radius, (0,0,255))
                r_norm = radius*normalize
                PCRC = r_norm
                print("PCRC Radius: %.2f mm" % r_norm)


                #show image
                cv2.imshow(i, img)
                points = []
                return True, AA, max_thickness, ACRC, PCRC
            else:
                #insufficient points
                return False, None, None, None, None

