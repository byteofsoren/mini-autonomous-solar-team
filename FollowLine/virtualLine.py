# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 11:04:36 2018

@author: Ulrik Åkesson
"""

import vrep, time, sys, array
from PIL import Image as I
from matplotlib import pyplot as plt
import numpy as np
from fuzzyPID import fuzzyPID as fPID
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
    KpSteering = 0.005
    KiSteering = 0
    KdSteering = 0.0005
    
    KpSpeed = 0.7
    KiSpeed = 0
    KdSpeed = 0.25
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
    dt = 0.02
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
    maxSpeed = 50
    minSpeed = 5
    
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
    # =============================================================================
    #   Camera used for Canny and virtual line
    # =============================================================================
    returnCode, camera = vrep.simxGetObjectHandle(clientID, 'mastCamera', vrep.simx_opmode_blocking)
    if returnCode != vrep.simx_return_ok:
        sys.exit('Could not get handle to sensor middle')
    # =============================================================================
    #   Lasers used for distance measurement and obstacle detection
    # =============================================================================
    returnCode, laserLeft = vrep.simxGetObjectHandle(clientID, 'mastLaserLeft', vrep.simx_opmode_blocking)
    if returnCode != vrep.simx_return_ok:
        sys.exit('Could not get handle to the left laser')
    returnCode, laserMiddle = vrep.simxGetObjectHandle(clientID, 'mastLaserMiddle', vrep.simx_opmode_blocking)
    if returnCode != vrep.simx_return_ok:
        sys.exit('Could not get handle to the middle laser')
    returnCode, laserRight = vrep.simxGetObjectHandle(clientID, 'mastLaserRight', vrep.simx_opmode_blocking)
    if returnCode != vrep.simx_return_ok:
        sys.exit('Could not get handle to the right laser')
          
# =============================================================================
#     Set initial heading and velocity
# =============================================================================
    returnCode = vrep.simxSetJointTargetPosition(clientID, steeringLeft, desiredSteeringAngle, vrep.simx_opmode_streaming)
    returnCode = vrep.simxSetJointTargetPosition(clientID, steeringRight, desiredSteeringAngle, vrep.simx_opmode_streaming)
    returnCode = vrep.simxSetJointTargetVelocity(clientID, motorLeft, desiredSpeed, vrep.simx_opmode_streaming)
    returnCode = vrep.simxSetJointTargetVelocity(clientID, motorRight, desiredSpeed, vrep.simx_opmode_streaming)
    
# =============================================================================
#     Initialize video stream
# =============================================================================
    returnCode, resolution, imageMiddle = vrep.simxGetVisionSensorImage(clientID, camera, 0, vrep.simx_opmode_streaming)
# =============================================================================
#     Initialize proximity stream
# =============================================================================
    returnCode, detectionStateLeft, detectedPointLeft, detectedObjectHandle, detectedSurfaceNormalVector = vrep.simxReadProximitySensor(clientID, laserLeft, vrep.simx_opmode_streaming)
    returnCode, detectionStateMiddle, detectedPointMiddle, detectedObjectHandle, detectedSurfaceNormalVector = vrep.simxReadProximitySensor(clientID, laserMiddle, vrep.simx_opmode_streaming)
    returnCode, detectionStateRight, detectedPointRight, detectedObjectHandle, detectedSurfaceNormalVector = vrep.simxReadProximitySensor(clientID, laserRight, vrep.simx_opmode_streaming)
    time.sleep(1) # Allow vrep som time to start streaming data

# =============================================================================
#     Until simulation closes run script
# =============================================================================
    while vrep.simxGetConnectionId(clientID) != -1:
# =============================================================================
#   Read lasers to decide between behaviour avoid obstacle or follow line
# =============================================================================
        objectLeft, distanceLeft = detectObject(clientID, laserLeft)
        objectMiddle, distanceMiddle = detectObject(clientID, laserMiddle)
        objectRight, distanceRight = detectObject(clientID, laserRight)
# =============================================================================
#       Obstacle Avoidance Behaviour
# =============================================================================
        if objectLeft or objectMiddle or objectRight:
            if objectLeft and objectRight:
                if prevDirection == 0:
                    e = 0.183*3
                    prevDirection = 1
                else:
                    e = -0.183*3
                    prevDirection = 0
                distance = (distanceLeft+distanceRight)/2
            elif objectMiddle:
                e = -0.0915*2
                distance = distanceMiddle
            elif objectLeft:
                e = -0.0915*2
                distance = distanceLeft
            elif objectRight:
                e = 0.0915*2
                distance = distanceRight
            print(distance)
            desiredSteeringAngle = np.arctan(e/distance)
            steeringAngleLeft = np.arctan(l/(-d+l/np.tan(desiredSteeringAngle)))
            steeringAngleRight = np.arctan(l/(d+l/np.tan(desiredSteeringAngle)))
            returnCode = vrep.simxSetJointTargetPosition(clientID, steeringLeft, steeringAngleLeft, vrep.simx_opmode_streaming)
            returnCode = vrep.simxSetJointTargetPosition(clientID, steeringRight, steeringAngleRight, vrep.simx_opmode_streaming)    
            returnCode = vrep.simxSetJointTargetVelocity(clientID, motorLeft, desiredSpeed, vrep.simx_opmode_streaming)
            returnCode = vrep.simxSetJointTargetVelocity(clientID, motorRight, desiredSpeed, vrep.simx_opmode_streaming)
            time.sleep(dt)
# =============================================================================
#       Follow Line behaviour
# =============================================================================
        else:
# =============================================================================
#           Read fotage from video buffer
# =============================================================================
            returnCode, resolution, image = vrep.simxGetVisionSensorImage(clientID, camera, 0, vrep.simx_opmode_buffer)
            if returnCode == vrep.simx_return_ok:
# =============================================================================
#               Store the resolution in a column and row variable
# =============================================================================
                cols = resolution[0]
                rows = resolution[1]
# =============================================================================
#               Convert image to a suitable format for openCV
# =============================================================================
                imageByteArray = bytes(array.array('b', image))
                imageBuffer = I.frombuffer("RGB", (cols,rows ), imageByteArray, "raw", "RGB", 0, 1)
                img2 = np.asarray(imageBuffer)
# =============================================================================
#               Convert image to grayscale
# =============================================================================
                img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
# =============================================================================
#               Smooth the image with Gaussian blur
# =============================================================================
                img2 = cv2.blur(img2, (3,3))
# =============================================================================
#               Do edgedetection with canny
# =============================================================================
                img2 = cv2.Canny(img2, 45, 100)
# =============================================================================
#               Algorithm for drawing a virtual line
# =============================================================================
                center = int(cols/2)
                left = 0
                right = 0
                middle = center;
                mean = 0
                minPx = 20
                maxPx = 50
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
# =============================================================================
#               Calculate the error between the middle of the road and the centerline of the car
# =============================================================================
                middle = mean/(maxPx-minPx)
                error = center-middle
                for idx in range(minPx, maxPx+1):
                        img2[idx, int(middle)] = 190
                plt.imshow(img2, cmap = "viridis", origin = "lower")
                plt.show()
            elif returnCode == vrep.simx_return_novalue_flag:
                print('No data yet')
                pass
            else:
                sys.exit('Could not get image')
# =============================================================================
#       Set integral and derivative term
# =============================================================================
            integral = integral+error*dt
            de = error-prevError
            derivative = (de)/dt
# =============================================================================
#       PID controller
# =============================================================================
# =============================================================================
#             Steering
# =============================================================================
            desiredSteeringAngle = KpSteering*error+KiSteering*integral+KdSteering*derivative
            if desiredSteeringAngle > maxSteeringAngle:
                desiredSteeringAngle = maxSteeringAngle
            elif desiredSteeringAngle < minSteeringAngle:
                desiredSteeringAngle = minSteeringAngle
            prevError = error
# =============================================================================
#             Speed
# =============================================================================
            desiredSpeed = maxSpeed-np.absolute(KpSpeed*error+KiSpeed*integral+KdSpeed*derivative)
            if desiredSpeed < minSpeed:
                desiredSpeed = minSpeed
# =============================================================================
#       Set steering angle
# =============================================================================
            print('Error', error)
            print('Change of error', de)
            print('Desired Steering Angle', desiredSteeringAngle)
            print('Desired Speed', desiredSpeed)
            steeringAngleLeft = np.arctan(l/(-d+l/np.tan(desiredSteeringAngle)))
            steeringAngleRight = np.arctan(l/(d+l/np.tan(desiredSteeringAngle)))
    
            returnCode = vrep.simxSetJointTargetPosition(clientID, steeringLeft, steeringAngleLeft, vrep.simx_opmode_streaming)
            returnCode = vrep.simxSetJointTargetPosition(clientID, steeringRight, steeringAngleRight, vrep.simx_opmode_streaming)    
            returnCode = vrep.simxSetJointTargetVelocity(clientID, motorLeft, desiredSpeed, vrep.simx_opmode_streaming)
            returnCode = vrep.simxSetJointTargetVelocity(clientID, motorRight, desiredSpeed, vrep.simx_opmode_streaming)
# =============================================================================
#             KpSteering, KdSteering = fPID(error, de)
#             print(KpSteering, KdSteering)
# =============================================================================
            time.sleep(dt)
    print('End of simulation')

def detectObject(clientID, sensorHandle):
    returnCode, detectionState, detectedPoint, detectedObjectHandle, detectedSurfaceNormalVector = vrep.simxReadProximitySensor(clientID, sensorHandle, vrep.simx_opmode_buffer)
    if returnCode == vrep.simx_return_ok:
        return detectionState, detectedPoint[2]
    elif returnCode == vrep.simx_return_novalue_flag:
        print('No value distance value yet')
        return False, -1
    else:
        sys.exit('Could not get distance reading')    
    
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