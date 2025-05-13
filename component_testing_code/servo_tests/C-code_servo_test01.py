#!/usr/bin/python
#
# version for RPi-flex_PCB 3WD robot
# C-code_servo_test01.py - C code + Python servo control with softPwm.h PWM and powered from RPi
# moves a SG90 servo with softPwm.h PWM from -nn deg to + nn deg positions - but has some dither
# SG90 servo has 3 wires: brown  -  GND
#                         red    -  5V supply
#                         orange -  PWM signal/control
#
# command:  python3 /home/pi3wdrobot/servo_tests/C-code_servo_test01.py
#

global debug
global spos_last   # used to avoid unnecessary servo 'dither'
global installed

global servo_mindc
global servo_middc
global servo_maxdc

debug = 2
spos_last = "none"


# ******************************
#   servo control function
# ******************************
def servopos(position):
    global debug
    global spos_last   # used to avoid unnecessary servo 'dither'
    global installed
    global servo_mindc
    global servo_middc
    global servo_maxdc

    # check if servo installed and do nothing if not
    if installed['servo'] == 'yes':
        # check if position is one of 3 standard strings
        if position == "min" or position == "mid" or position == "max":
            if position == "min" and position != spos_last:
                RPiflex01_gpio.set_pwm(pwm_pin, servo_mindc)   # move servo to the min position
                spos_last = "min"
                if debug == 2:
                    print ("servopos: servo moved to min - " + str(servo_mindc) )
            elif position == "max" and position != spos_last:
                RPiflex01_gpio.set_pwm(pwm_pin, servo_maxdc)   # move servo to the min position
                spos_last = "max"
                if debug == 2:
                    print ("servopos: servo moved to max - " + str(servo_maxdc) )
            elif position == "mid" and position != spos_last:
                RPiflex01_gpio.set_pwm(pwm_pin, servo_middc)   # move servo to the min position
                spos_last = "mid"
                if debug == 2:
                    print ("servopos: servo moved to mid - " + str(servo_middc) )
        # now check if position is an 'angle' i.e. a servo command in the integer range 2 to 15
        elif int(position) > 2 and int(position) < 15:
            RPiflex01_gpio.set_pwm(pwm_pin, int(position))    # move servo to the 'angle' position
            spos_last = position
            if debug == 2:
                print ("servopos: servo moved to angle position - " + str(position) )
        else :
            print ("unknown servo position - no action taken")

#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# function to read the current installed options from its log file 
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def readinstalls():
    # open default file to read
    installfile = open("/home/pi3wdrobot/logfiles/RPi-flex_logs/RPi-flex_installed.txt", "r") # file path hardcoded
    readinstalls = installfile.read()
    installed = eval(readinstalls)
    print ("\n installed components set up \n")
    # close the log file
    installfile.close()
    return(installed);


# ******************************
#   main code
# ******************************

import time               # this imports the module to allow various time functions to be used

# allow C libraries to be used
from ctypes import *

# for GPIO functions the custom C library is used which uses the wiringPi functions
RPiflex01_gpio = CDLL("/home/pi3wdrobot/RPi-flex_pi_PCB_robot/libRPiflex03_gpio.so")
#call C function to check connection to gpio C library
RPiflex01_gpio.connect() 
# set the Broadcom pin numbering
RPiflex01_gpio.set_broadcom()

debug = 2
spos_last = "none"

# Get the various installed options from the log file
installed = readinstalls()

pwm_pin = 19    # this is the GPIO pin used for servo control connected to GPIO#19 (servo 1) on the RPi-flex PCB

# initialise PWM pin
RPiflex01_gpio.setPWM_GPIO(pwm_pin)

# set the min and max duty cycles for the servo
servo_mindc = 8   # needs to be less than 1ms pulses ie <5% duty cycle - see the support documentation for more details
servo_middc = 14   # needs to be 1.5ms pulses ie 7.5% duty cycle - see the support documentation for more details
servo_maxdc = 20  # needs to be more than 2ms pulses ie >10% duty cycle - see the support documentation for more details

RPiflex01_gpio.set_pwm(pwm_pin, servo_middc)
print("middle position")
time.sleep(3)
		
print("Program running: moves the servo from min to max continuously - CTRL C to stop")
try:    # this loop is not strictly necessary but it does allow the script to be easily stopped with CTRL-C
    while True:  # this is the continuous loop
        servopos("max")    # move servo to the max position
        print("maximum position")
        time.sleep(2)

        servopos("mid")    # move servo to the mid position
        print("middle position")
        time.sleep(2)

        servopos("min")    # move servo to the min position
        print("minimum position")
        time.sleep(2)

        servopos("mid")    # move servo back to the mid position
        print("middle position")
        time.sleep(2)

finally:  # this code is run when the try is interrupted with a CTRL-C
    servopos("mid")    # move servo back to the mid position
    print(" ")
    print(" ")
    print(" ")
    time.sleep(1)
    
