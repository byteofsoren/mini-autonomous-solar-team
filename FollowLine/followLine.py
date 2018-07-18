# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 11:04:36 2018

@author: Ulrik Åkesson
"""

import vrep,time,sys
import numpy as np

def followLine(clientID):
# =============================================================================
#     Initialize constants and variables
# =============================================================================
    d = 0.0944
    l = 0.322
    r = 0.04
    sensorsLeft = [-1, -1, -1, -1]
    sensorsRight = [-1, -1, -1, -1]
    imagesLeft = [-1, -1, -1, -1]
    imagesRight = [-1, -1, -1, -1]
    detectionLeft = [-1, -1, -1, -1]
    detectionRight = [-1, -1, -1, -1]
    Kp = 10
    Ki = 1
    Kd = 1
    error = 0
    prevError = 0
    integral = 0
    derivative = 0
    dt = 0.05
    desiredSteeringAngle = 0
    maxSteeringAngle = 50*np.pi/180
    minSteeringAngle = -1*maxSteeringAngle
    desiredSpeed = 8
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
    returnCode, sensorMiddle = vrep.simxGetObjectHandle(clientID, 'mastMiddleSensor', vrep.simx_opmode_blocking)
    if returnCode != vrep.simx_return_ok:
        sys.exit('Could not get handle to sensor middle')
    for i in range(4):
        returnCode, sensorsLeft[i] = vrep.simxGetObjectHandle(clientID, 'mastLeftError%d' % (i), vrep.simx_opmode_blocking)
        if returnCode != vrep.simx_return_ok:
            sys.exit('Could not get handle to left sensor %d' % (i))
        returnCode, sensorsRight[i] = vrep.simxGetObjectHandle(clientID, 'mastRightError%d' % (i), vrep.simx_opmode_blocking)
        if returnCode != vrep.simx_return_ok:
            sys.exit('Could not get handle to right sensor %d' % (i))
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
    returnCode, resolution, imageMiddle = vrep.simxGetVisionSensorImage(clientID, sensorMiddle, 1, vrep.simx_opmode_streaming)
    for i in range(4):
        returnCode, resolution, imagesLeft[i] = vrep.simxGetVisionSensorImage(clientID, sensorsLeft[i], 1, vrep.simx_opmode_streaming)
        returnCode, resolution, imagesRight[i] = vrep.simxGetVisionSensorImage(clientID, sensorsRight[i], 1, vrep.simx_opmode_streaming)
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
#     Check the proximity sensors to decide the behaviour 
# =============================================================================
        objectLeft, distanceLeft = detectObject(clientID, laserLeft)
        objectMiddle, distanceMiddle = detectObject(clientID, laserMiddle)
        objectRight, distanceRight = detectObject(clientID, laserRight)
        if objectLeft or objectMiddle or objectRight:
            while objectLeft or objectMiddle or objectRight:
                if objectLeft and objectRight:
                    e = 0.183*3
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
                desiredSteeringAngle = np.arctan(e/distance)
                steeringAngleLeft = np.arctan(l/(-d+l/np.tan(desiredSteeringAngle)))
                steeringAngleRight = np.arctan(l/(d+l/np.tan(desiredSteeringAngle)))
                returnCode = vrep.simxSetJointTargetPosition(clientID, steeringLeft, steeringAngleLeft, vrep.simx_opmode_streaming)
                returnCode = vrep.simxSetJointTargetPosition(clientID, steeringRight, steeringAngleRight, vrep.simx_opmode_streaming)    
                returnCode = vrep.simxSetJointTargetVelocity(clientID, motorLeft, desiredSpeed, vrep.simx_opmode_streaming)
                returnCode = vrep.simxSetJointTargetVelocity(clientID, motorRight, desiredSpeed, vrep.simx_opmode_streaming)
                time.sleep(dt)
                objectLeft, distanceLeft = detectObject(clientID, laserLeft)
                objectMiddle, distanceMiddle = detectObject(clientID, laserMiddle)
                objectRight, distanceRight = detectObject(clientID, laserRight)
                
            t = distance/(desiredSpeed*r)
            iterations = int(np.ceil(t/(2*dt)))
# =============================================================================
#             print('Desired Steering Angle', desiredSteeringAngle)
# =============================================================================
            for i in range(iterations):
# =============================================================================
#                 string = "{} of {}".format(i, iterations)
#                 print(string)
# =============================================================================
                time.sleep(dt)
                
            desiredSteeringAngle *= -1
# =============================================================================
#             print('Desired Steering Angle', desiredSteeringAngle)
# =============================================================================
            steeringAngleLeft = np.arctan(l/(-d+l/np.tan(desiredSteeringAngle)))
            steeringAngleRight = np.arctan(l/(d+l/np.tan(desiredSteeringAngle)))
            returnCode = vrep.simxSetJointTargetPosition(clientID, steeringLeft, steeringAngleLeft, vrep.simx_opmode_streaming)
            returnCode = vrep.simxSetJointTargetPosition(clientID, steeringRight, steeringAngleRight, vrep.simx_opmode_streaming)    
            returnCode = vrep.simxSetJointTargetVelocity(clientID, motorLeft, desiredSpeed, vrep.simx_opmode_streaming)
            returnCode = vrep.simxSetJointTargetVelocity(clientID, motorRight, desiredSpeed, vrep.simx_opmode_streaming)
            for i in range(iterations*2):
# =============================================================================
#                 string = "{} of {}".format(i, iterations*2)
#                 print(string)
# =============================================================================
                time.sleep(dt)
                
            desiredSteeringAngle *= 1.5
            print('Desired Steering Angle', desiredSteeringAngle)
            steeringAngleLeft = np.arctan(l/(-d+l/np.tan(desiredSteeringAngle)))
            steeringAngleRight = np.arctan(l/(d+l/np.tan(desiredSteeringAngle)))
            returnCode = vrep.simxSetJointTargetPosition(clientID, steeringLeft, steeringAngleLeft, vrep.simx_opmode_streaming)
            returnCode = vrep.simxSetJointTargetPosition(clientID, steeringRight, steeringAngleRight, vrep.simx_opmode_streaming)    
            returnCode = vrep.simxSetJointTargetVelocity(clientID, motorLeft, desiredSpeed, vrep.simx_opmode_streaming)
            returnCode = vrep.simxSetJointTargetVelocity(clientID, motorRight, desiredSpeed, vrep.simx_opmode_streaming)
            for i in range(iterations):
# =============================================================================
#                 string = "{} of {}".format(i, iterations)
#                 print(string)
# =============================================================================
                time.sleep(dt)
            
            integral = 0
# =============================================================================
#             for i in range(iterations):
#                 string = "{} of {}".format(i, iterations)
#                 print(string)
#                 time.sleep(dt)
# =============================================================================
        else: #Run follow line behaviour
# =============================================================================
#     Read sensors detecting the line
# =============================================================================
            detectionMiddle = detectLine(clientID, sensorMiddle)
            for i in range(4):
                detectionLeft[i] = detectLine(clientID, sensorsLeft[i])
                detectionRight[i] = detectLine(clientID, sensorsRight[i])
        
# =============================================================================
#         Determine the error based on the sensor values
# =============================================================================
            if detectionMiddle:
                error = 0
            if detectionLeft[0]:
                error = 0.015
            if detectionRight[0]:
                error = -0.015
            if detectionLeft[1]:
                error = 0.03
            if detectionRight[1]:
                error = -0.03
            if detectionLeft[2]:
                error = 0.045
            if detectionRight[2]:
                error = -0.045
            if detectionLeft[3]:
                error = 0.06
            if detectionRight[3]:
                error = -0.06    
# =============================================================================
#       Set integral and derivative term
# =============================================================================
            integral = integral+error*dt
            derivative = (error-prevError)/dt
# =============================================================================
#       PID controller
# =============================================================================
            desiredSpeed = maxSpeed - 3*np.absolute((Kp*error+Ki*integral+Kd*derivative))
            desiredSteeringAngle = Kp*error+Ki*integral+Kd*derivative
            if desiredSteeringAngle > maxSteeringAngle:
                desiredSteeringAngle = maxSteeringAngle
            elif desiredSteeringAngle < minSteeringAngle:
                desiredSteeringAngle = minSteeringAngle
            prevError = error
# =============================================================================
#       Set steering angle
# =============================================================================
            print('Desired Speed', desiredSpeed)
            steeringAngleLeft = np.arctan(l/(-d+l/np.tan(desiredSteeringAngle)))
            steeringAngleRight = np.arctan(l/(d+l/np.tan(desiredSteeringAngle)))
    
            returnCode = vrep.simxSetJointTargetPosition(clientID, steeringLeft, steeringAngleLeft, vrep.simx_opmode_streaming)
            returnCode = vrep.simxSetJointTargetPosition(clientID, steeringRight, steeringAngleRight, vrep.simx_opmode_streaming)    
            returnCode = vrep.simxSetJointTargetVelocity(clientID, motorLeft, desiredSpeed, vrep.simx_opmode_streaming)
            returnCode = vrep.simxSetJointTargetVelocity(clientID, motorRight, desiredSpeed, vrep.simx_opmode_streaming)
            time.sleep(dt)
    print('End of simulation')


    
def detectLine(clientID, sensorHandle):
    returnCode, resolution, image = vrep.simxGetVisionSensorImage(clientID, sensorHandle, 1, vrep.simx_opmode_buffer)
    if returnCode == vrep.simx_return_ok:
        im = np.array(image, dtype=np.uint8)
        return im < 30
    elif returnCode == vrep.simx_return_novalue_flag:
        print('No data yet')
        return False
    else:
        sys.exit('Could not get image')
        
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
    vrep.simxFinish(-1)
    clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5)
    if clientID!=-1:
        print('Connected to remote API server')
        followLine(clientID)

    else:
        print('Connection non successful')
        sys.exit('Could not connect')