"""This is a template for Sign Detector modules.

   A Sign Detector module is a python file that contains a `detect` function
   that is capable of analyzing a color image which, according to the image
   server, likely contains a road sign. The analysis should identify the kind
   of road sign contained in the image.

   See the description of the `detect` function below for more details.

   Please note: implementors are free to add additional (auxiliary) methods and
   variables to the file (called from within the detect() function)
"""

import logging
import numpy as np
import cv2

logging.info('Template SignDetector has been initialized')


def detect(bb, sign):
    """This function receives:
    - sign: a color image (numpy array of shape (h,w,3))
    - bb which is the bounding box of the sign in the original camera frame
      bb = (x0,y0, w, h) where w and h are the widht and height of the sign
      (can be used to determine e.g., whether the sign is to the left or
       right of the car's center)
    The goal of this method is to recognize which of the following signs it
    really is:
    - a stop sign
    - a turn left sign
    - a turn right sign
    - None, if the sign is determined to be none of the above

    Returns: a dictionary that contains information about the recognized
    sign. This dict is transmitted to the state machine it should contain
    all the information that the state machine to act upon the sign (e.g.,
    the type of sign, estimated distance).
    """
    
    (x0, y0, w, h) = bb
    b,g,r = cv2.split(sign)
    t = 0
    matrice_a_gauche, matrice_a_droite = np.array_split(b, 2, 1)
    somme_g = np.sum(matrice_a_gauche)
    somme_d = np.sum(matrice_a_droite)
    if w/h > 0.5 and w/h < 1.4:

        if len(r[r > 80]) > w*h//3 and len(b[b < 60]) > w*h//3 :
            t = "Stop"
        elif len(b[b > 81]) > w*h//3:
            if somme_g > somme_d + 100 :
                t = "Left"
            else : 
                t = "Right"
    sign_dict = {'sign' : t, 'x0' : x0, 'y0' : y0, 'w' : w, 'h' : h}
    return sign_dict
    
