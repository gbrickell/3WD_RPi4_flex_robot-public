#!/usr/bin/python
# 
# version for RPi-flex_PCB 3WD robot
# command to run:  python3 /home/pi3wdrobot/ultrasonic_sensor/sensor-C-distance.py

#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# individual ultrasonic sensor control functions 
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# Take a distance measurement 
def Measure(): 
    # set the Trigger LOW for a period 
    RPiflex02_gpio.setlow_ultra(pinTrigger, 100000, debug) # 100 ms settling period
    # send a 10us HIGH to trigger the sensor's ranging program (which sends 8 ultrasound bursts at 40 kHz)
    RPiflex02_gpio.send_ultra(pinTrigger, 10, debug)
    InitTime = time.time()
    StartTime = time.time() 
    StopTime = StartTime
    tooshort = "no"
    abort = "no"

    # now record the timestamp for the latest ECHO LOW
    while RPiflex02_gpio.read_pin(pinEcho)==0: 
        StartTime = time.time() 
        StopTime = StartTime
        if StartTime-InitTime > 2.0: # taking too long to capture 1st timestamp
            print ("Abort: taking >2s to capture 1st timestamp measurement")
            abort = "yes"
            Distance = 0.0
            return (Distance, tooshort, abort)

    while RPiflex02_gpio.read_pin(pinEcho)==1: 
        StopTime = time.time() 
        # If the sensor is too close to an object, the Pi cannot 
        # see the echo quickly enough, so it misses the response and waits and 
        # waits setting a 'trip' time that is unrealistically long so the code can  
        # detect the missed signal problem and say what has happened 
        if StopTime-StartTime >= 0.04:   # a time of 0.04 implies >6.8m !
            print("Hold on there! Return pulse missed or you're too close.") 
            tooshort = "yes"
            Distance = 0.0
            return (Distance, tooshort, abort)

    ElapsedTime = StopTime - StartTime 
    Distance = (ElapsedTime * 34326)/2    # speed of sound in air is 343.26 m/s so distance is in cm
    #print ("Distance: " + str(Distance) )
    return (Distance, tooshort, abort)

#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# Return True if the ultrasonic sensor sees an obstacle within its HowNear limit
def IsNearObstacle(localHowNear): 
    # try 5 times to get a non-zero Distance reading
    sensetry = 0
    goodresult = 0
    while goodresult == 0:
        sensetry = sensetry +1
        Distance, tooshort, abort = Measure()   # use Measure function
        if (Distance > 0.0 and tooshort != "yes" and abort != "yes") or sensetry >=5 :
            goodresult = 1
            print ("sensetry: " + str(sensetry) + " - Distance: " + str(Distance) )

    if tooshort == "yes":
        print ("Obstacle distance: too short to measure")
    elif abort == "yes":
        print ("Missed time stamp - read aborted")
    #else:
    #    print ("Obstacle distance: " + str(Distance)) 
    if Distance < localHowNear and tooshort == "no": 
        print ("** Need to avoid object **")
        return True 
    else: 
        return False


#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# main code
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


import time # Import the Time library
import datetime

# allow C libraries to be used
from ctypes import *

# for GPIO functions the custom C library is used which uses the wiringPi functions
RPiflex02_gpio = CDLL("/home/pi3wdrobot/RPi-flex_pi_PCB_robot/libRPiflex03_gpio.so")
#call C function to check connection to gpio C library
RPiflex02_gpio.connect() 
# set the Broadcom pin numbering
RPiflex02_gpio.set_broadcom()

debug = 0   # outputs more info to the screen: set to 0 once code is in production use

# Define GPIO pins to use on the Pi
pinTrigger = 27
pinEcho = 22

print("Ultrasonic Measurement")

# set the Trigger and Echo pins as OUTPUT and INPUT respectively
RPiflex02_gpio.setIO_GPIO(pinTrigger, 1)   # Trigger 
RPiflex02_gpio.setIO_GPIO(pinEcho, 0)      # Echo

try:
    # Repeat the next indented block forever
    while True:
        IsNearObstacle(5.0)

# If you press CTRL+C, cleanup and stop
except KeyboardInterrupt:
    # Reset GPIO settings
    pass
