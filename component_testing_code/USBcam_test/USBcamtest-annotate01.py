#!/usr/bin/python
#
# image annotating version for RPi-flex_PCB mecanum wheeled 4WD robot
# USBcamtest-annotate01.py - Flask USB camera test routine
#
# command:  python3 /home/RPi_system_code/USBcam_test/USBcamtest-annotate01.py
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
        for i in range (0, 8):  # loop thru a series of servo angles
            servo.start(servoangle[i]) # pan the camera to the next setting
            time.sleep(0.3) # small pause to allow the camera position to steady
            for j in range (0,15):  # now take 15 frames at each pan position
                servostream = str(servopos[i])
                frame = camera.get_frame(servostream)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
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

import time # Import the Time library
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

pwm_servo = 19     # this is the GPIO pin used for servo control connected to GPIO#19 (servo 1) on the RPi-flex PCB v4

################################
# servo set up
################################
# set the min and max duty cycles for the servo
servo_mindc = 4   # needs to be less than 1ms pulses ie <5% duty cycle - see the support documentation for more details
servo_middc = 6.8   # needs to be 1.5ms pulses ie 7.5% duty cycle - see the support documentation for more details
servo_maxdc = 9.5  # needs to be more than 2ms pulses ie >10% duty cycle - see the support documentation for more details

GPIO.setup(pwm_servo, GPIO.OUT)  # set the GPIO PWM pin as an output
servo = GPIO.PWM(pwm_servo, 50)  # set PWM on the control GPIO pin with frequency 50Hz
servo.start(servo_middc)   # sets an initial duty cycle to move servo to the central position
print("servo: middle position")

# set the various servo 'angles' to be used for camera 'panning' - 8 position cycle starting dead ahead
servoangle = [6.8, 5.4, 4, 5.4, 6.8, 8.15, 9.5, 8.15]
servopos = ["0", "+30", "+60", "+30", "0", "-30", "-60", "-30"]


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
    print ('Interrupted')
    print ("Cleaning up at the end of the program")

