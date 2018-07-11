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
    d = 0.0944
    l = 0.322
    r = 0.04
    prevDirection = 0
    Kp = 0.01
    Ki = 0
    Kd = 0
    error = 0
    prevError = 0
    integral = 0
    derivative = 0
    dt = 0.05
    desiredSteeringAngle = 0
    maxSteeringAngle = 50*np.pi/180
    minSteeringAngle = -1*maxSteeringAngle
    desiredSpeed = 20
    #minSpeed = 0
    maxSpeed = 8
    
# =============================================================================
#     Initalize handles to motors
# =============================================================================
    returnCode, steeringLeft = vrep.simxGetObjectHandle(clientID, 'mastSteeringLeft', vrep.simx_opmode_blocking)
    if returnCode != vrep.simx_return_ok:
        sys.exit('Could not get handle to steering left')
    returnCode, steeringRight = vrep.simxGetObjectHandle(clientID, 'mastSteeringRight', vrep.simx_opmode_blocking)
    if returnCode != vrep.simx_return_ok:
        sys.exit('Could not get handle to steering right')
    returnCode, motorLeft = vrep.simxGetObjectHandle(clientID, 'mastMotorLeft', vrep.simx_opmode_blocking)
    if returnCode != vrep.simx_return_ok:
        sys.exit('Could not get handle to motor left')
    returnCode, motorRight = vrep.simxGetObjectHandle(clientID, 'mastMotorRight', vrep.simx_opmode_blocking)
    if returnCode != vrep.simx_return_ok:
        sys.exit('Could not get handle to motor right')
        
# =============================================================================
#   initialize handles to sensors
# =============================================================================
    returnCode, camera = vrep.simxGetObjectHandle(clientID, 'mastCamera', vrep.simx_opmode_blocking)
    if returnCode != vrep.simx_return_ok:
        sys.exit('Could not get handle to sensor middle')
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
        objectLeft, distanceLeft = detectObject(clientID, laserLeft)
        objectMiddle, distanceMiddle = detectObject(clientID, laserMiddle)
        objectRight, distanceRight = detectObject(clientID, laserRight)
        
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

        else: #Run follow line behaviour
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
                center = int(cols/2)
                left = 0
                right = 0
                middle = center;
                mean = 0
                minPx = 20
                maxPx = 45
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
            derivative = (error-prevError)/dt
# =============================================================================
#       PID controller
# =============================================================================
# =============================================================================
#           desiredSpeed = maxSpeed - 3*np.absolute((Kp*error+Ki*integral+Kd*derivative))
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
            print('Desired Steering Angle', desiredSteeringAngle)
            steeringAngleLeft = np.arctan(l/(-d+l/np.tan(desiredSteeringAngle)))
            steeringAngleRight = np.arctan(l/(d+l/np.tan(desiredSteeringAngle)))
    
            returnCode = vrep.simxSetJointTargetPosition(clientID, steeringLeft, steeringAngleLeft, vrep.simx_opmode_streaming)
            returnCode = vrep.simxSetJointTargetPosition(clientID, steeringRight, steeringAngleRight, vrep.simx_opmode_streaming)    
            returnCode = vrep.simxSetJointTargetVelocity(clientID, motorLeft, desiredSpeed, vrep.simx_opmode_streaming)
            returnCode = vrep.simxSetJointTargetVelocity(clientID, motorRight, desiredSpeed, vrep.simx_opmode_streaming)
            time.sleep(dt)
    print('End of simulation')

    
    
if __name__ == '__main__':
    vrep.simxFinish(-1)
    clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5)
    if clientID!=-1:
        print('Connected to remote API server')
        followLine(clientID)

    else:
        print('Connection non successful')
        sys.exit('Could not connect')