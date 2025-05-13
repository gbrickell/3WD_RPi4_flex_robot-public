#!/usr/bin/python
# 

# command to run:  python3 /home/pi3wdrobot/sw_header_tests/switch_test-v2.py

import RPi.GPIO as GPIO # Import the GPIO Library
import time # Import the Time library

# Set the GPIO modes
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set variables slide switches connected to the GPIO pins using the flexbot PCB
onoff = 14
AB = 23
CD = 18
EF = 15

# Set the on/off slide switch as an input
GPIO.setup(onoff, GPIO.IN)

# Set AB, CD & EF slide switches as an inputs
GPIO.setup(AB, GPIO.IN)
GPIO.setup(CD, GPIO.IN)
GPIO.setup(EF, GPIO.IN)


# set some parameters so that the program only prints out something if it has changed from last time
state_onoff = 2
state_AB = 2
state_CD = 2
state_EF = 2

try:
    #repeat the next indented block forever
    while True:
        # if the on/off switch is low (=0), it's off
        if GPIO.input(onoff)==0 and state_onoff!=0:
            print('The on/off switch is OFF')
            state_onoff = 0

        # If not (else), print the following
        elif GPIO.input(onoff)==1 and state_onoff!=1:
            print('The on/off switch is ON')
            state_onoff = 1

        # if the AB switch is low (=0), it's set to B
        if GPIO.input(AB)==0 and state_AB!=0:
            print('switch AB set to B')
            state_AB = 0

        # If not (else), print the following
        elif GPIO.input(AB)==1 and state_AB!=1:
            print('switch AB set to A')
            state_AB = 1

        # if the CD switch is low (=0), it's set to D
        if GPIO.input(CD)==0 and state_CD!=0: 
            print('switch CD set to D')
            state_CD = 0

        # If not (else), print the following
        elif GPIO.input(CD)==1 and state_CD!=1:
            print('switch CD set to C')
            state_CD = 1

        # if the EF switch is low (=0), it's set to F
        if GPIO.input(EF)==0 and state_EF!=0:
            print('switch EF set to F')
            state_EF = 0

        # If not (else), print the following
        elif GPIO.input(EF)==1 and state_EF!=1:
            print('switch EF set to E')
            state_EF = 1

        # Wait, then do the same again
        time.sleep(0.2)

# If you press CTRL+C, cleanup and stop
except KeyboardInterrupt:
    GPIO.cleanup()
