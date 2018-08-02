Authour: Ulrik Åkesson
Date: 2018-07-31

Summary:
The controller between the TX2 and the car, impelemented on a roboRIO.
This code will handle actuating the servo and the ESC of the car.

Topics:
    to_rio
    from_rio
    emegency_stop_internal

Messages:
    to_rio:
       float64 set_speed
       float64 set_steering
       int8 enable
       time time_frame
    from_rio:
       float64[4] set_speed
       float64[4] set_steering
       int8 error
       string error_message
       time time_frame
    vehicle_emergency_stop:
       int8 emergency_stop = 0 