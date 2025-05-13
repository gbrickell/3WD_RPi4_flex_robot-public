#!/usr/bin/python
# 
# check for each slide switch setting
# opmode_last is a simple passed parameter of the current/last opmode setting
# opmode = 0 means 'idle' with the ON/OFF switch in the OFF position - but not checked here
# opmode = 1 means ON + ACE
# opmode = 2 means ON + BCE
# opmode = 3 means ON + ADE
# opmode = 4 means ON + ADF
# opmode = 5 means ON + ACF
# opmode = 6 means ON + BCF
# opmode = 7 means ON + BDE
# opmode = 8 means ON + BDF
# opmode = 9 means an undefined operational mode


# command to run:  python3 /home/pi3wdrobot/sw_header_tests/switch_C_test-v2.py

import time # Import the Time library

# allow C libraries to be used
from ctypes import *
debug = 1   # outputs more info to the screen: set to 0 once code is in production use
# for GPIO functions the custom C library is used which uses the wiringPi functions
flexbot01_gpio = CDLL("/home/pi3wdrobot/RPi-flex_pi_PCB_robot/libRPiflex03_gpio.so")
#call C function to check connection to gpio C library
flexbot01_gpio.connect() 
# set the Broadcom pin numbering
flexbot01_gpio.set_broadcom(debug)

# Set variables slide switches connected to the GPIO pins using the flexbot PCB
onoff = 14
AB = 23
CD = 18
EF = 15

print (" slide switch/header socket GPIOs: " + str(onoff) + " - " + str(AB) + " - " + str(CD) + " - " + str(EF) )

# set the slide switch pins as INPUT
flexbot01_gpio.setIO_GPIO(onoff, 0, debug)
flexbot01_gpio.setIO_GPIO(AB, 0, debug)
flexbot01_gpio.setIO_GPIO(CD, 0, debug)
flexbot01_gpio.setIO_GPIO(EF, 0, debug)

# set initial switch states to something undefined so that the program checks can run from the start
state_onoff = 2
state_AB = 2
state_CD = 2
state_EF = 2

# get an initial swmode and opmode setting
global swmode   # swmode variable set as global just in case
global opmode   # opmode variable set as global just in case

# initially send a swmode_last and 'opmode_last' of 10 that is 'impossible'
swmode = flexbot01_gpio.check_onoff(10, debug, onoff)
opmode = flexbot01_gpio.check_slideswitch(10, debug, AB, CD, EF)
swmode_last = swmode
opmode_last = opmode
print ("initial swmode - opmode: " + str(swmode) + " - " + str(opmode) )

printstatus = "yes"  # set initial condition
loop = 0

try:
    #repeat the next indented block forever
    while True:
        swmode = flexbot01_gpio.check_onoff(swmode_last, debug, onoff)
        opmode = flexbot01_gpio.check_slideswitch(opmode_last, debug, AB, CD, EF)
        swmode_last = swmode
        opmode_last = opmode

        # if the on/off switch is low (=0), it's off
        if swmode==0 and state_onoff!=0:
            print('The on/off switch is in the STOP position')
            state_onoff = 0

        # If not (else), print the following
        elif swmode==1 and state_onoff!=1:
            print('The on/off switch is in the GO position')
            state_onoff = 1

        # if the opmode has changed print out the switch settings
        if opmode != opmode_last:
            print('opmode: ' + str(opmode))
            opmode_last = opmode
            if opmode == 1:
                print ("switch settings: ACE")
            elif opmode == 2:
                print ("switch settings: BCE")
            elif opmode == 3:
                print ("switch settings: ADE")
            elif opmode == 4:
                print ("switch settings: ADF")
            elif opmode == 5:
                print ("switch settings: ACF")
            elif opmode == 6:
                print ("switch settings: BCF")
            elif opmode == 7:
                print ("switch settings: BDE")
            elif opmode == 8:
                print ("switch settings: BDF")
            elif opmode == 9:
                print ("switch settings: undefined")

        # Wait, then do the same again
        time.sleep(0.2)

# If you press CTRL+C, cleanup and stop
except KeyboardInterrupt:
    print ("program stopped")
