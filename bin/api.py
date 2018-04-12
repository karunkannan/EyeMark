"""
Author: Karun Kannan
Last Update: 3/23/18
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
        #cv2.imshow("Image Displayer", img)

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
def _calc_center_of_points(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    #calc the center
    c_x = (x2 + x1)/2
    c_y = (y2 + y1)/2
    #calc perp point, defined as v
    mag = _distance((c_x, c_y), pt2)
    multiplier = _distance((c_x, c_y), points[5])
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
    h = _distance(pt1, pt2)
    a = _distance(pt1, (x, c_y))
    alpha = np.arccos(a/h)
    alpha = 180*alpha/np.pi
    if c_y > y:
        return -1*alpha
    else:
        return alpha

''' Find center of a circle given 3 points
    Method: System of 3 equations to solve for x_c, y_c, r
    Variable C, A from proof written in pdf (not in github, will appear in
    publication in future)
    Param: Three points of form (x,y)
    Return: Center (x_c, y_c) and radius
'''
def _calc_center_of_circle(pt1, pt2, pt3):
    x1, y1 = pt1
    x2, y2 = pt2
    x3, y3 = pt3

    #calculate C
    C = (x2**2 - x1**2) + (y2**2 - y1**2) - (x2 - x1)*((x3**2 - x1**2 + y3**2 -
        y1**2)/(x3 - x1))

    #Calculate A
    A = 2*(y2 - y1 - ((y3 - y1)*(x2 - x1)/(x3 - x1)))
    #NOTE: subtract the third term!

    #Calculate y_c
    y_c = C/A

    #Calculate x_c
    x_c = ((x3**2 - x1**2 + y3**2 - y1**2 - 2*y_c*(y3 - y1))/(2*(x3 - x1)))

    #Calculate the radius

    r = np.sqrt((x1 - x_c)**2 + (y1 - y_c)**2)

    return (int(x_c), int(y_c)), r

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
        6,7: Outer base radius points
        '''
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            cv2.destroyAllWindows()
            if len(points) == 8:
                dist = np.float32(input('What is the control distance of this image?: '))
                normalize = np.divide(np.float32(dist),
                    np.float32(_distance(points[0], points[1])))

                #draw AA line
                cv2.line(img, points[2], points[3], (255,0,0), 1)
                #compute AA line length
                AA = np.float32(_distance(points[2], points[3]))*normalize
                print("AA distance is %.2f mm" % AA)

                #draw central line
                #TODO: Deal with cutoff images, idea: slide center point once drawn
                c, perp_point = _calc_center_of_points(points[2], points[3])
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
                center_point_ACRC, radius_ACRC = _calc_center_of_circle(
                        points[6], points[7], points[5])
                cv2.circle(img, center_point_ACRC, int(radius_ACRC), (0,0,255))
                r_norm = radius_ACRC*normalize
                ACRC = r_norm
                print("ACRC radius: %.2f mm" % r_norm)

                #PCRC
                center_point_PCRC, radius_PCRC = _calc_center_of_circle(
                        points[2], points[3], points[4])
                cv2.circle(img, center_point_PCRC, int(radius_PCRC), (0,0,255))
                r_norm = radius_PCRC*normalize
                PCRC = r_norm
                print("PCRC Radius: %.2f mm" % r_norm)

                ##Depth of AC
                depth_of_AC = _distance(c, points[4])
                depth_of_AC = depth_of_AC*normalize
                print("Depth of AC: %.2f mm" % depth_of_AC)


                #show image
                cv2.imshow("Processed", img)
                points = []
                return True, float(AA), float(max_thickness), float(ACRC), float(PCRC), float(depth_of_AC)
            else:
                #insufficient points
                points = []
                return False, None, None, None, None, None
        elif k == ord('d'):
            img = img_copy
            points = points[1:len(points)]
        elif k == ord('r'):
            points = []
            img = cv2.imread(fname)
            img_copy = img.copy()
        elif k == ord('e'):
            return True, None, None, None, None, None



