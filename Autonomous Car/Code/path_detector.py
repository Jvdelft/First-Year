"""This is a simplistic Path Detector.

    A Path Detector module is a python file that contains a `detect` function
    that is capable of analyzing a binarized image in which non-zero pixels
    indicate road boundaries. The analysis should identify the path (or,
    multiple paths) to follow.

    See the description of the `detect` function below for more details.

    This Simplistic Path Detector implements a first crude idea to path
    detection, and needs ample modification in order to obtain a working
    prototype.

    In this Simplistic Path Detector, a path is detected by sampling a single
    row towards the bottom of the image. Non-zero pixels are identified to
    infer the road between the car center and the road center is calculated and
    used as the path to follow. """

import logging
import numpy as np
import cv2
import time 
from scipy import ndimage


# Log which path detector is being used. This appears in the output. Useful
# for ensuring that the correct path detector is being used.
logging.info('Bacar0 ZEN is ready for departure')


def detect(mask):
    """This function receives a binarized image in its `mask` argument
    (`mask` is a h x w  numpy array where h is the height and w the width).
    The non-zero pixels in the array encode road boundaries.

    The task of this function is to analyze the mask, and identify the path
    that the car should follow.

    Returns: a tuple (dict, img) where:
      `dict` is a dictionary that is transmitted to the state machine
           it should contain all the information that the state machine
           requires to actuate the identified path(s).
           Implementors are free to encode this information in the dictionary
           in any way that they like. Of course, the state machine needs to
           be written correspondingly to correctly decode the information.

      `img` is optionally a numpy array (of the same width and height
            as the mask) that visualizes the found path. Used for
            visualization in the viewer only.
    """

    img_height, img_width = mask.shape
    x0 = int(img_width / 2)  # center of the image
    # row to sample (first row at the top is row zero)
    y0 = int(img_height*0.65)

    # assume the car center is at coordinate (img_width/2, img_height)
    car_center = (x0, img_height)

    # assure no obstacle is in front of the car. In order to do this,we take several
    # points on the vertical line passing through the centre of the car and a couple
    # to the left and the right of the car. It covers a greater area so the
    # possiblity of the car swerving because of noise is unlikely. These are marked
    # in pink

    dead_center = (int(img_width/2) , int(img_height/2) )
    delta = 12           
    ref0 = ( x0 , y0 )
    ref1 = ( x0 , int(y0 - delta) )
    ref2 = ( x0 , int(y0 - 1.5*delta))
    ref3 = ( x0 , int(y0 - 2*delta))
    ref4 = ( x0 , int(y0 - 2.5*delta))
    ref5 = ( x0 , int(y0 - 3*delta))
    ref6 = ( x0 , int(y0 - 4*delta))
    ref7 = (int(x0 - delta) , int(y0 - delta) )
    ref8 = (int(x0 + delta) , int(y0 - delta) )

    ref_list = [ ref1 , ref2 , ref3 , ref4 , ref5, ref6 , ref7, ref8]
    

    # If the car approaches an obstacle, we must check the surroundings to the left
    # and to the right. These points are marked yellow

    left1 = ( int(x0-2.5*delta) , int(y0-delta) )
    left2 = ( int(x0-2.5*delta) , int(y0-1.5*delta) )
    left3 = ( int(x0-2.5*delta) , int(y0-2.5*delta) )
    left4 = ( int(x0-3*delta) , int(y0-1.5*delta) )
    left_list = [left1, left2, left3, left4 ]

    right1 = ( int(x0+2.5*delta) , int(y0-delta) )
    right2 = ( int(x0+2.5*delta) , int(y0-1.5*delta) )
    right3 = ( int(x0+2.5*delta) , int(y0-2.5*delta) )
    right4 = ( int(x0+3*delta) , int(y0-1.5*delta) )
    right_list = [right1, right2, right3, right4 ]

    #If the car approaches an intersaction where it can go left or right, it will
    #detect those directions and know it is possible to turn in this direction. To do
    #so, a series of dots are marked in cyan on bird's view map and are used to tell
    #if those are non zero.

    cross1L = ( int(x0-3.4*delta) , int(y0-3*delta) )
    cross2L = ( int(x0-3.6*delta) , int(y0-2.5*delta) )
    cross3L = ( int(x0-3.9*delta) , int(y0-2*delta) )
    cross4L = ( int(x0-3.6*delta) , int(y0-1.5*delta) )
    cross5L = ( int(x0-3.4*delta) , int(y0-1*delta) )
    cross6R = ( int(x0+3.4*delta) , int(y0-3*delta) )
    cross7R = ( int(x0+3.6*delta) , int(y0-2.5*delta) )
    cross8R = ( int(x0+3.9*delta) , int(y0-2*delta) )
    cross9R = ( int(x0+3.6*delta) , int(y0-1.5*delta) )
    cross10R = ( int(x0+3.4*delta) , int(y0-1*delta) )
    cross_left=[cross1L,cross2L,cross3L,cross4L,cross5L]
    cross_right = [cross6R, cross7R, cross8R, cross9R, cross10R ]
    #A couple of points are used to predict the road far ahead. If the points are on 
    #the road (the are mostly zeros) the the car will continue ahead without
    #interference

    far1 = ( x0, 0 )
    far2 = (int(x0-.8*delta), int(.5*delta) )
    far3 = (int(x0+.8*delta), int(.5*delta) )
    far4 = (int(x0-1.6*delta), int(delta))
    far5 = (int(x0+1.6*delta), int(delta))
    far_list = [far1, far2, far3, far4, far5 ]

    #Verify the car can turn left or right if the sign given by the path_detector says
    #so
    
    left_o = 0
    right_o= 0
    clear_left = False
    clear_right = False

    for this in cross_left:
        if int(mask[this[1]][this[0]]) == 0:
            left_o = left_o + 1
    for that in cross_right:
        if int(mask[that[1]][that[0]]) == 0:
            right_o = right_o + 1
    

    #First case: no obstacles found in front of the car: find the road centre and
    #directs towards it
   
    obstacle_det = 0
    for elem in ref_list:
        if int(mask[elem[1]][elem[0]]) != 0:
            obstacle_det = obstacle_det + 1

    if left_o >= 4 and obstacle_det <= 3:
        clear_left = True
    if right_o >=4 and obstacle_det <= 3:
        clear_right = True

    if obstacle_det <= 3:
     
        far_obst = 0
        for dot in far_list:
            if int(mask[dot[1]][dot[0]]) != 0:
                far_obst = far_obst + 1
      
        #If the road is straight as far as the camera can see, the car will go straight
        if far_obst == 0:
        
            heading = 0
            road_center = dead_center
            path_dict = {'heading': heading, 'car_center': car_center, 'clear_left': clear_left, 'clear_right': clear_right }
            path_img = np.zeros((img_height, img_width, 3), np.uint8)

        else:

            # try to find the road center by sampling the horizontal line passing
            # through (x0,y0) -- find_center is a function defined further below
            road_center = find_center(mask, x0, y0)

            # calculate the angle between the vertical line that passes through
            # the car center and the line that connects the car center with the road
            # center -- model_to_heading is a function further defined below
            heading = model_to_heading(road_center, car_center)

            # send the calculated information to the state machine
            # NOTE: one may want to extend the analysis and measure, e.g., how
            # reliable the path is (in other words: how long one thinks one could
            # follow it.) If this is measured one may also want to include it in
            # this dictionary so that the state
            # machine can use this.
            path_dict = {'heading': heading, 'car_center': car_center, 'clear_left': clear_left, 'clear_right': clear_right }
 
            # uncomment the following line if you want to print the dictionary
            # for debugging purposes
            # logging.debug('returning %s' % str(path_dict))

            # for debugging purposes, we visualize the above process
 
            # create a new image, of the same dimensions as mask, but colore
            path_img = np.zeros((img_height, img_width, 3), np.uint8)

        
    
    #If the car detects an obstacle, the it will use the yellow dots to guide itself: 
    #if the path is clear to the right, the it will go right. If the path is clear to
    #the left, it will go left. 
    

    elif obstacle_det > 3:

        left_obst = 0
        right_obst= 0
        for point in left_list:
            if int(mask[point[1]][point[0]]) != 0:
                left_obst = left_obst + 1
        for k in right_list:
            if int(mask[k[1]][k[0]]) != 0:
                right_obst = right_obst + 1
        if right_obst < 2:
            heading = -12
        elif left_obst <2:
            heading = 12
        
        

    #If the car detects an obstacle and it can not go neither left or right, the it is 
    #a dead end and the car will turn around 
 
        elif right_obst >= 2 and left_obst >= 2:
             heading = 16

        path_dict = {'heading': heading, 'car_center': car_center, 'clear_left': clear_left, 'clear_right': clear_right }
        # create a new image, of the same dimensions as mask, but colore
        path_img = np.zeros((img_height, img_width, 3), np.uint8)
        road_center = ( 0, y0 )



    # Draw a small filled dot at the car center, 4 pixels wide, in blue
    cv2.circle(path_img, car_center, 4, (255, 0, 0), -1)

    # Draw a green line to display the row that was sampled
    cv2.line(path_img, (0, y0), (img_width, y0), (0, 255, 0))

    # Draw a small filled dot at the calculated road center, 4 pixels wide,
    # in red
    cv2.circle(path_img, road_center, 4, (0, 0, 255), -1)

    # Draw a small pink dot for each point used for obstacle detection

    cv2.circle(path_img, ref0 , 3 , (180,105,255), -1)
    cv2.circle(path_img, ref1 , 2 , (180,105,255), -1)
    cv2.circle(path_img, ref2 , 2 , (180,105,255), -1)
    cv2.circle(path_img, ref3 , 2 , (180,105,255), -1)
    cv2.circle(path_img, ref4 , 2 , (180,105,255), -1)
    cv2.circle(path_img, ref5 , 2 , (180,105,255), -1)
    cv2.circle(path_img, ref6 , 2 , (180,105,255), -1)  
    cv2.circle(path_img, ref7 , 2 , (180,105,255), -1)
    cv2.circle(path_img, ref8 , 2 , (180,105,255), -1)
   
    # Draw a small yellow dot for each point used for emergency steering

    cv2.circle(path_img, left1 , 2, (0,255,255), -1)
    cv2.circle(path_img, left2 , 2, (0,255,255), -1)
    cv2.circle(path_img, left3 , 2, (0,255,255), -1)
    cv2.circle(path_img, left4 , 2, (0,255,255), -1)
    cv2.circle(path_img, right1, 2, (0,255,255), -1)
    cv2.circle(path_img, right2, 2, (0,255,255), -1)
    cv2.circle(path_img, right3, 2, (0,255,255), -1)
    cv2.circle(path_img, right4, 2, (0,255,255), -1)

    #Draw a small cyan dot for every cross point used to detect 3 and 4 way crossses

    cv2.circle(path_img, cross1L, 2, (255,255,0), -1)
    cv2.circle(path_img, cross2L, 2, (255,255,0), -1)
    cv2.circle(path_img, cross3L, 2, (255,255,0), -1)
    cv2.circle(path_img, cross4L, 2, (255,255,0), -1)
    cv2.circle(path_img, cross5L, 2, (255,255,0), -1)
    cv2.circle(path_img, cross6R, 2, (255,255,0), -1)
    cv2.circle(path_img, cross7R, 2, (255,255,0), -1)
    cv2.circle(path_img, cross8R, 2, (255,255,0), -1)
    cv2.circle(path_img, cross9R, 2, (255,255,0), -1)
    cv2.circle(path_img, cross10R, 2, (255,255,0), -1)

    #Draw a small red dot for every point used to detect the road far ahead 

    cv2.circle(path_img, far1, 2, (0,0,255), -1)
    cv2.circle(path_img, far2, 2, (0,0,255), -1)
    cv2.circle(path_img, far3, 2, (0,0,255), -1)
    cv2.circle(path_img, far4, 2, (0,0,255), -1)
    cv2.circle(path_img, far5, 2, (0,0,255), -1)


    # Return the path dictionary and image. The path_dict will be sent
    # to the state machine. The path_img is displayed in the viewer
    return (path_dict, path_img)


def find_center(mask, x, y):
    """Sample the horizontal line passing through coordinate (x,y) for non-zero
       pixels in mask to determine road center"""
    img_height, img_width = mask.shape
    sample_width = int(img_width / 2)
    p0 = np.array([x, y])
    pl = np.array([x-sample_width, y])
    pr = np.array([x+sample_width, y])

    # Take 40 samples on the left and 40 samples on the right
    # profile is a function further defined below
    xl, yl, l_val = profile(mask, p0, pl, 60)
    xr, yr, r_val = profile(mask, p0, pr, 60)

    # now analyze the sampling: find the first non-zero pixel in the samples
    idx_l = np.nonzero(l_val)[0]
    idx_r = np.nonzero(r_val)[0]

    if idx_l.size == 0:
        # No non-zero pixel was found on the left. This means that we don't
        # see the left hand side of the road on row y0
        # arbitrarily set the road boundary at x = x0 - 30
        # this parameter value (30) likely needs to be tuned
        contact_l = p0 + np.array([-30, 0])
    else:
        # Interpret the first non-zero pixel as the road boundary
        contact_l = np.array([xl[idx_l[0]], yl[idx_l[0]]])

    if idx_r.size == 0:
        contact_r = p0 + np.array([30, 0])
    else:
        contact_r = np.array([xr[idx_r[0]], yr[idx_r[0]]])

    # we define the road center to be mid-way contact_l and contact_r
    center = (contact_l + contact_r) / 2
    return (int(center[0]), int(center[1]))


def model_to_heading(model_xy, car_center_xy):
    """Calculate the angle (in degrees) between the vertical line that
       passes through the point `car_center_xy` and the line that connects
       `car_center_xy` with `model_xy`.
       A negative angle means that the car should turn clockwise; a positive
       angle that the car should move counter-clockwise."""
    dx = 1. * model_xy[0] - car_center_xy[0]
    dy = 1. * model_xy[1] - car_center_xy[1]

    heading = -np.arctan2(dx, -dy)*180/np.pi

    return heading


def profile(mask, p0, p1, num):
    """Takes `num` equi-distance samples on the straight line between point `p0`
       and point `p2` on binary image `mask`.

       Here, points p0 and p1 are 2D points (x-coord,y-coord)

       Returns: a triple (n, m, vals) where:
       - n is a numpy array of size `num` containing the x-coordinates of
         sampled points
       - m is a numpy array of size `num` containing the y-coordinates of
         sampled points
       - vals is a numpy array of size `num` containing the sampled point
         values, i.e.  vals[i] = mask[m[i], n[i]]
         (recall that images are indexed first on y-coordinate, then on
          x-coordinate)
     """
    n = np.linspace(p0[0], p1[0], num)
    m = np.linspace(p0[1], p1[1], num)
    return [n, m, ndimage.map_coordinates(mask, [m, n], order=0)]
