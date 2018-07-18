# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 11:04:36 2018

@author: Ulrik Åkesson
"""

import vrep, time, sys, array
from PIL import Image as I
from matplotlib import pyplot as plt
import numpy as np
import cv2

def followLine(clientID):
# =============================================================================
#     Initialize constants and variables
# =============================================================================
    # =============================================================================
    #     Constants related to the dynamics of the robot
    # =============================================================================
    d = 0.0944
    l = 0.322
    r = 0.04
    # =============================================================================
    #     Variable used for obstacleavoidance
    # =============================================================================
    prevDirection = 0
    # =============================================================================
    #     PID Gains, fine for now but will need further tuning
    # =============================================================================
    Kp = 0.001
    Ki = 0
    Kd = 0
    # =============================================================================
    #     Varaiables related to the PID-controller
    # =============================================================================
    error = 0
    prevError = 0
    integral = 0
    derivative = 0
    # =============================================================================
    #     Discrete time for the simulation at 50ms
    # =============================================================================
    dt = 1/40
    # =============================================================================
    #     Initial steering angle and speed
    # =============================================================================
    desiredSteeringAngle = 0
    desiredSpeed = 50
    # =============================================================================
    #     Limits to steering angle and speed
    # =============================================================================
    maxSteeringAngle = 50*np.pi/180
    minSteeringAngle = -1*maxSteeringAngle
    maxSpeed = 8
    minSpeed = 0
    
# =============================================================================
#     Initalize handles to motors
# =============================================================================
    # =============================================================================
    #     Steering
    # =============================================================================
    returnCode, steeringLeft = vrep.simxGetObjectHandle(clientID, 'mastSteeringLeft', vrep.simx_opmode_blocking)
    if returnCode != vrep.simx_return_ok:
        sys.exit('Could not get handle to steering left')
    returnCode, steeringRight = vrep.simxGetObjectHandle(clientID, 'mastSteeringRight', vrep.simx_opmode_blocking)
    if returnCode != vrep.simx_return_ok:
        sys.exit('Could not get handle to steering right')
    # =============================================================================
    #   Driving
    # =============================================================================
    returnCode, motorLeft = vrep.simxGetObjectHandle(clientID, 'mastMotorLeft', vrep.simx_opmode_blocking)
    if returnCode != vrep.simx_return_ok:
        sys.exit('Could not get handle to motor left')
    returnCode, motorRight = vrep.simxGetObjectHandle(clientID, 'mastMotorRight', vrep.simx_opmode_blocking)
    if returnCode != vrep.simx_return_ok:
        sys.exit('Could not get handle to motor right')
        
# =============================================================================
#   initialize handles to sensors
# =============================================================================
    cap = cv2.VideoCapture('GoKart.mp4')
    # =============================================================================
    #   Lasers used for distance measurement and obstacle detection
    # =============================================================================
# =============================================================================
#     Set initial heading and velocity
# =============================================================================
    returnCode = vrep.simxSetJointTargetPosition(clientID, steeringLeft, desiredSteeringAngle, vrep.simx_opmode_streaming)
    returnCode = vrep.simxSetJointTargetPosition(clientID, steeringRight, desiredSteeringAngle, vrep.simx_opmode_streaming)
    returnCode = vrep.simxSetJointTargetVelocity(clientID, motorLeft, desiredSpeed, vrep.simx_opmode_streaming)
    returnCode = vrep.simxSetJointTargetVelocity(clientID, motorRight, desiredSpeed, vrep.simx_opmode_streaming)
    
# =============================================================================
#     Initialize proximity stream
# =============================================================================
    
    time.sleep(1) # Allow vrep som time to start streaming data

# =============================================================================
#     Until simulation closes run script
# =============================================================================
    while vrep.simxGetConnectionId(clientID) != -1:
# =============================================================================
#           Read fotage from video buffer
# =============================================================================
        ret, img2 = cap.read()


        cols = 1280
# =============================================================================
#             rows = 720
# =============================================================================

        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        img2 = cv2.blur(img2, (3,3))

        img2 = cv2.Canny(img2, 45, 100)

        center = int(cols/2)+50
        left = 0
        right = 0
        middle = center;
        mean = 0
        minPx = 400
        maxPx = 500
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
            img2[jdx, center] = 128

        middle = mean/(maxPx-minPx)
        for idx in range(minPx, maxPx+1):
            img2[idx, int(middle)] = 190
        error = center-middle
        cv2.imshow('stream', img2)
        cv2.waitKey(1)
# =============================================================================
#         plt.imshow(img2, cmap = "viridis")
#         plt.show()
# =============================================================================
# =============================================================================
#       Set integral and derivative term
# =============================================================================
        integral = integral+error*dt
        derivative = (error-prevError)/dt
# =============================================================================
#       PID controller
# =============================================================================
        desiredSteeringAngle = Kp*error+Ki*integral+Kd*derivative
        if desiredSteeringAngle > maxSteeringAngle:
            desiredSteeringAngle = maxSteeringAngle
        elif desiredSteeringAngle < minSteeringAngle:
            desiredSteeringAngle = minSteeringAngle
        prevError = error
# =============================================================================
#       Set steering angle
# =============================================================================
# =============================================================================
#             print('Desired Steering Angle', desiredSteeringAngle)
# =============================================================================
        steeringAngleLeft = np.arctan(l/(-d+l/np.tan(desiredSteeringAngle)))
        steeringAngleRight = np.arctan(l/(d+l/np.tan(desiredSteeringAngle)))

        returnCode = vrep.simxSetJointTargetPosition(clientID, steeringLeft, steeringAngleLeft, vrep.simx_opmode_streaming)
        returnCode = vrep.simxSetJointTargetPosition(clientID, steeringRight, steeringAngleRight, vrep.simx_opmode_streaming)    
        returnCode = vrep.simxSetJointTargetVelocity(clientID, motorLeft, desiredSpeed, vrep.simx_opmode_streaming)
        returnCode = vrep.simxSetJointTargetVelocity(clientID, motorRight, desiredSpeed, vrep.simx_opmode_streaming)
        time.sleep(dt)
    print('End of simulation')
    cap.release()
    cv2.destroyAllWindows()

# =============================================================================
# def detectObject(clientID, sensorHandle):
#     returnCode, detectionState, detectedPoint, detectedObjectHandle, detectedSurfaceNormalVector = vrep.simxReadProximitySensor(clientID, sensorHandle, vrep.simx_opmode_buffer)
#     if returnCode == vrep.simx_return_ok:
#         return detectionState, detectedPoint[2]
#     elif returnCode == vrep.simx_return_novalue_flag:
#         print('No value distance value yet')
#         return False, -1
#     else:
#         sys.exit('Could not get distance reading')    
#     
# =============================================================================
if __name__ == '__main__':
# =============================================================================
#   Open connection to V-REP
# =============================================================================
    vrep.simxFinish(-1)
    clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5)
    if clientID!=-1:
        
        print('Connected to remote API server')
        followLine(clientID)

    else:
        print('Connection non successful')
        sys.exit('Could not connect')