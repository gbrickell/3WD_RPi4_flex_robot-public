#!/usr/bin/python
#
# version for RPi-flex_PCB omni-wheeled 3WD robot
# syspwm_servo_test01.py - Python only servo control using syspwm (https://github.com/jdimpson/syspwm) 
#  and powered from RPi movng a SG90 servo from -nn deg to + nn deg positions
# SG90 servo has 3 wires: brown  -  GND
#                         red    -  5V supply
#                         orange -  PWM signal/control

#
# command:  sudo python3 /home/pi3wdrobot/servo_tests/syspwm_test01.py
#


from syspwm import SysPWM    # this imports the custom PWM library installed in the same folder
import time                  # this imports the module to allow various time functions to be used
import sys,os
import atexit

SLEE=0.02
PAUS=2
FREQ=20

#S=0.65
S=0.85
E=2.30
M=1.6

#pwm0 is GPIO pin 18 is physical pin 12
#pwm0 = SysPWM(0)
#pwm0.disable()

#pwm1 is GPIO pin 19 is physical pin 35
pwm = SysPWM(1)
pwm.set_frequency(FREQ)
time.sleep(1)
pwm.set_duty_cycle(M)
#atexit.register(pwm.disable) # using a try/finally loop instead
pwm.enable()
time.sleep(PAUS)

intS = int(S*100)
intE = int(E*100)
print("Program running: moves the servo from max (S) to min (E) continuously - CTRL C to stop")
try:    # this loop is not strictly necessary but it does allow 
        #  the script to be easily stopped with CTRL-C
    while True:
        for i in range(intS,intE):
            pwm.set_duty_cycle(i/100.0)
            #print (i-intS)
            time.sleep(SLEE)
        time.sleep(PAUS)
        for i in range(intE,intS,-1):
            pwm.set_duty_cycle(i/100.0)
            #print (i-intS)
            time.sleep(SLEE)
        time.sleep(PAUS)
finally:  # this code is run when the try is interrupted with a CTRL-C
    pwm.set_duty_cycle(M)    # move servo back to the mid position
    print(" ")
    print(" ")
    pwm.disable
    print(" ")
    print(" ")
    time.sleep(1)
