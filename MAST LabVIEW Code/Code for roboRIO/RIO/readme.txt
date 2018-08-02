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
    from_rio:
       float64 set_speed
       float64 set_steering
    vehicle_emergency_stop:
       uint8 emergency_stop = 0 