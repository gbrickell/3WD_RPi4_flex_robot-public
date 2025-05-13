#!/usr/bin/python
#
# image annotating version for RPi-flex_PCB 3WD robot
#  - using the hardware PWM custom library syspwm.py stored in the same folder
# USBcamtest-hw-PWM_annotate01.py - Flask USB camera test routine
#
# command:  sudo python3 /home/pi3wdrobot/USBcam_test/USBcamtest-hw-PWM_annotate01.py
#

#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# function to generate the video stream from the camera 
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def gen(camera):
    """Video streaming generator function."""
    global stop_streaming
    global servostream

    while not stop_streaming:
        frame = camera.get_frame(servostream)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    time.sleep(0.1) 
    print ("streaming stopped")

#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# function to generate the video stream from the camera whilst it pans from left to right
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def genpan(camera):
    """Video streaming generator function."""
    global stop_streaming
    global servostream
    global servoangle
    global servopos
    global servo

    while not stop_streaming:
        for i in range (0, 12):  # loop thru a series of servo angles
            pwm.set_duty_cycle(servoangle[i]) # pan the camera to the next setting
            print ("now at servo position: " + str(servopos[i]))
            servostream = str(servopos[i])
            time.sleep(0.1) # small pause to allow the camera position to steady
            for j in range (0,10):  # now several images at the current pan position
                frame = camera.get_frame(servostream)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            # now pause to let the camera display catch up before moving again
            print ("10 images taken at servo position: " + str(servopos[i]))
            time.sleep(0.2)
    time.sleep(0.1) 
    print ("streaming stopped")



#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# main code 
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# /etc/fstab should have been edited to set up a ram drive for the robot image streaming .jpg files
# it should be something like the text below so that both root and the user can read/write to the folder
# none    /mnt/robot_ramimage    ramfs    noauto,user,size=2M,mode=0770    0    0
#   /mnt/robot_ramimage is a mount point, where the ramfs filesystem will be mounted and this directory should exist.
#   noauto option prevents this to be mounted automatically (e.g. at system's boot up)
#   user makes this mountable by individual regular users
#   size sets this "ramdisk's" size
#   mode is very important, with the octal code 0770 only root and the user who mounted this filesystem, will be able to 
#    read and write to the drive, not the others 
#   PLEASE NOTE only one user can use the ram drive at any one time!

from syspwm import SysPWM    # this imports the custom PWM library installed in the same folder
import time                  # this imports the module to allow various time functions to be used
import sys,os
import atexit
import datetime

global servostream
global servoangle
global servopos
servostream = ""

################################
# GPIO set up
################################
import RPi.GPIO as GPIO # Import the GPIO Library - still using this ???
# Set the GPIO modes using GPIO 
GPIO.setmode(GPIO.BCM) 
GPIO.setwarnings(False) 

#pwm1 is GPIO pin 19 is physical pin 35
pwm = SysPWM(1)
pwm.set_frequency(20)
pwm.set_duty_cycle(1.6)  # start at the mid-way position
#atexit.register(pwm.disable)  # using a try/finally loop instead
pwm.enable()
print("servo: middle position")
time.sleep(2)

pwm_servo = 19   # no longer used but this is the GPIO pin used for servo control connected to GPIO#19 (servo 1) on the RPi-flex PCB v4

################################
# servo set up
################################
# set the min and max duty cycles for the servo
servo_mindc = 0.85  # needs to be less than 1ms pulses ie <5% duty cycle - see the support documentation for more details
servo_middc = 1.55   # needs to be ~1.5ms pulses ie 7.5% duty cycle - see the support documentation for more details
servo_maxdc = 2.3   # needs to be more than 2ms pulses ie >10% duty cycle - see the support documentation for more details

# set the various servo 'angles' to be used for camera 'panning' - 8 position cycle starting dead ahead
servoangle = [1.6,  1.23,  0.85,  0.50,  0.85, 1.23, 1.55,  1.95,   2.3,   2.60,   2.3,  1.95]
servopos =   ["0", "+30", "+60", "+90", "+60", "+30", "0", "-30", "-60", "-90", "-60", "-30"]


################################
# Flask set up
################################
from flask import Flask, render_template  # as we are NOT using sudo must use a non-80 HTTP port
from flask import request
from flask import Response

# import the appropriate USB camera image streaming module
#from robot_camera_usb_opencv import Camera   # import the non-annotate custom openCV USB camera class with image annotation function
from robot_camera_usb_opencv_annotate import Camera   # import the custom openCV USB camera class with image annotation function

RPi_flex_app01 = Flask(__name__)  # creates a Flask object called RPi_flex_app01 for the web server operation


try:        

    # for this simple test code the following very large while-loop is just continuously running

    #####################
    #  start of main loop
    #####################
    while True:

        ###############################################################################
        # this route goes to the selection mode routine when the URL root is selected
        ###############################################################################
        @RPi_flex_app01.route("/") # run the code below this function when the URL root is accessed
        def start():
            global stop_streaming
            global robot_name
            stop_streaming = False
            select_mode = "annotated video streaming",
            template_data = {
                'title' : select_mode,
            }
            return render_template('select_mode_justvideo.html', **template_data)
	
	
        ###############################################################################
        # this route provides the video streaming
        ###############################################################################
        @RPi_flex_app01.route('/video_feed/<int:pixwidth>/<int:pixheight>/<stopstream>/', methods=['GET'])  
        def video_feed(pixwidth, pixheight, stopstream):  # pixwidth, pixheight and stopstream passed from template
            """Video image streaming route - this is put in the src attribute of an img tag in the template"""
            global stop_streaming
            global robot_name
            global servostream
            global pansetting

            print ("start video streaming route - stop streaming: " + str(stopstream) )
            time.sleep(0.001) # pause for 1ms - produces a bit of a delay but ...

            stop_streaming = False   # now set the logical value used elsewhere
            return Response(genpan(Camera(pixwidth, pixheight)), mimetype='multipart/x-mixed-replace; boundary=frame')

            template_data = {
                'title' : "select options",
            }

            return render_template('select_mode_justvideo.html', **template_data)	

        ##################################################################################
        # the code below is the last code in the web part of the system
        ##################################################################################
        print ("starting web server")
        if __name__ == "__main__":
            RPi_flex_app01.run(host='0.0.0.0', port=8080, debug=False, threaded=True)   # 0.0.0.0 means any device on the network can access the web app

    # end of While loop

finally:  
    print ('Interrupted and resetting servo/pwm')
    time.sleep(2)
    pwm.set_duty_cycle(1.6)  # reset the servo to the mid-way position
    time.sleep(2)
    pwm.set_duty_cycle(1.6)  # reset the servo again as 'old' positioning may still be in a buffer
    pwm.disable()
    print ("Cleaning up at the end of the program")

