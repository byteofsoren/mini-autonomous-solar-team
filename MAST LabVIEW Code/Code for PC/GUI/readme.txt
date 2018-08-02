Authour: Ulrik Åkesson
Date: 2018-07-31

Summary:
The main interface between the host computer and the nvidia TX2,
which hosts the roboRIO.

Since the roboRIO is hidden behind the TX2 webinterface the idea is to use
a buffer node at the TX2 for cross communication.

Topics:
    vehicle_settings
    vehicle_status
    emegency_stop_external

Messages:
    vehicle_settings:
       int8 enable
        int8 run
        int8 gui_connection_requierd=1
        float64 max_speed=3.0
        time time_frame 
    vehicle_status:
       float64 speed_is
       float64[4] steering_is
       float64[3] distance_front
       float64[3] distance_back
       int8 error_id
       string  error_message
       time time_frame
       uint64 delta_tx2_rio
    vehicle_emergency_stop:
       uint8 emergency_stop = 0 