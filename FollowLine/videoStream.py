# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 09:24:33 2018

@author: Ulrik Åkesson
"""

import vrep, time, sys, array
from PIL import Image as I
from matplotlib import pyplot as plt
import numpy as np
import cv2


def videoStream(clientID):
# =============================================================================
#     returnCode, camera = vrep.simxGetObjectHandle(clientID, 'mastCamera', vrep.simx_opmode_blocking)
#     if returnCode != vrep.simx_return_ok:
#         sys.exit('Could not get handle to sensor middle')
#     returnCode, resolution, imageMiddle = vrep.simxGetVisionSensorImage(clientID, camera, 0, vrep.simx_opmode_streaming)
# =============================================================================
# =============================================================================
#     plt.figure()
# =============================================================================
    time.sleep(1)
    
    while vrep.simxGetConnectionId(clientID) != -1:
        returnCode, resolution, image = vrep.simxGetVisionSensorImage(clientID, camera, 0, vrep.simx_opmode_buffer)
        if returnCode == vrep.simx_return_ok:
            cols = resolution[0]
            rows = resolution[1]
            imageByteArray = bytes(array.array('b', image))
            imageBuffer = I.frombuffer("RGB", (cols,rows ), imageByteArray, "raw", "RGB", 0, 1)
            img2 = np.asarray(imageBuffer)
            img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            img2 = cv2.blur(img2, (3,3))
            img2 = cv2.Canny(img2, 45, 100)
# =============================================================================
#             print(resolution)
# =============================================================================
            center = int(cols/2)
            left = 0
            right = 0
            middle = center;
            mean = 0
            minPx = 40
            maxPx = 60
            for jdx in range(minPx, maxPx+1):
                if img2[jdx, middle] == 0:
                    for idx in range(middle, cols, 1):
                        if img2[jdx, idx] == 255 or idx == cols-1:
                            right = idx
                            break
                    for idx in range(middle-1, -1, -1):
                        if img2[jdx, idx] == 255 or idx == 0:
                            left = idx
                            break
                middle = int(round(right+(left-right)*0.5))
                mean += middle
                img2[jdx, middle] = 255
            middle = mean/(maxPx-minPx)
            error = center-middle
            print(error)
            
# =============================================================================
#             cv2.imshow("Stream", img2)
#             if cv2.waitKey(0) and vrep.simxGetConnectionId(clientID) != -1:
#                 break
# =============================================================================
            plt.imshow(img2, cmap = "viridis", origin = "lower")
            plt.show()
        elif returnCode == vrep.simx_return_novalue_flag:
            print('No data yet')
            pass
        else:
            sys.exit('Could not get image')
        
        time.sleep(0.05)
    
# =============================================================================
#     cv2.destroyAllWindows()
# =============================================================================

if __name__ == '__main__':
# =============================================================================
#     cv2.startWindowThread()
#     cv2.namedWindow("Stream")
# =============================================================================
    vrep.simxFinish(-1)
    clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5)
    if clientID!=-1:
        print('Connected to remote API server')
        videoStream(clientID)

    else:
        print('Connection non successful')
        sys.exit('Could not connect')