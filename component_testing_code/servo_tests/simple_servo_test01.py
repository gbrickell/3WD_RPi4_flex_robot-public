#!/usr/bin/python
#
# version for RPi-flex_PCB 3WD robot
# simple_servo_test01.py - simple Python only servo control with GPIO PWM and powered from RPi
# moves a SG90 servo with GPIO PWM from -nn deg to + nn deg positions
# SG90 servo has 3 wires: brown  -  GND
#                         red    -  5V supply
#                         orange -  PWM signal/control
#
# command:  python3 /home/pi3wdrobot/servo_tests/simple_servo_test01.py
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
                servo.ChangeDutyCycle(servo_mindc)    # move servo to the min position
                spos_last = "min"
                if debug == 2:
                    print ("servopos: servo moved to min - " + str(servo_mindc) )
            elif position == "max" and position != spos_last:
                servo.ChangeDutyCycle(servo_maxdc)    # move servo to the min position
                spos_last = "max"
                if debug == 2:
                    print ("servopos: servo moved to max - " + str(servo_maxdc) )
            elif position == "mid" and position != spos_last:
                servo.ChangeDutyCycle(servo_middc)    # move servo to the min position
                spos_last = "mid"
                if debug == 2:
                    print ("servopos: servo moved to mid - " + str(servo_middc) )
        # now check if position is an 'angle' i.e. a servo command in the integer range 2 to 15
        elif int(position) > 2 and int(position) < 15:
            servo.ChangeDutyCycle(int(position))    # move servo to the 'angle' position
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
import RPi.GPIO as GPIO   # this imports the module to allow the GPIO pins to be easily utilised

debug = 2
spos_last = "none"

# Get the various installed options from the log file
installed = readinstalls()


# This code sets the RPi to use the BCM (Broadcom) pin numbers which is usually the default but is positively set here
GPIO.setmode(GPIO.BCM)

pwm_pin = 19    # this is the GPIO pin used for servo control connected to GPIO#19 (servo 1) on the RPi-flex PCB

GPIO.setup(pwm_pin, GPIO.OUT)  # set the GPIO PWM pin as an output
servo = GPIO.PWM(pwm_pin, 50)  # set PWM on the control GPIO pin with frequency 50Hz

# set the min and max duty cycles for the servo
servo_mindc = 2.4   # needs to be less than 1ms pulses ie <5% duty cycle - see the support documentation for more details
servo_middc = 7   # needs to be 1.5ms pulses ie 7.5% duty cycle - see the support documentation for more details
servo_maxdc = 11.5  # needs to be more than 2ms pulses ie >10% duty cycle - see the support documentation for more details

servo.start(servo_middc)   # sets an initial duty cycle to move servo to the central position
print("middle position")
time.sleep(3)
		
print("Program running: moves the servo from min to max continuously - CTRL C to stop")
try:    # this loop is not strictly necessary but it does allow the script to be easily stopped with CTRL-C
    while True:  # this is the continuous loop
        servopos("max")    # move servo to the max position
        print("maximum position")
        time.sleep(1)

        servopos(7)    # move servo to the mid position
        print("middle position")
        time.sleep(1)

        servopos("min")    # move servo to the min position
        print("minimum position")
        time.sleep(1)

        servopos("mid")    # move servo back to the mid position
        print("middle position")
        time.sleep(1)

finally:  # this code is run when the try is interrupted with a CTRL-C
    servopos("mid")    # move servo back to the mid position
    print(" ")
    print("Cleaning up the GPIO pins before stopping")
    print(" ")
    print(" ")
    print(" ")
    time.sleep(1)
    servopos("mid")    # move servo back to the mid position again - just in case
    servo.stop()
    GPIO.cleanup()
    
# The cleanup command sets all the pins back to inputs which protects the
# Pi from accidental shorts-circuits if something metal touches the GPIO pins.

