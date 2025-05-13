#!/usr/bin/python
#
# non-annotating & non-rotating camera (servo) version for RPi-flex_PCB omni-wheeled 3WD robot
# USBcamtest01.py - Flask USB camera test routine
#
# command:  python3 /home/pi3wdrobot/USBcam_test/USBcamtest01.py
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
    print(servostream)
    while not stop_streaming:
        #frame = camera.get_frame(servostream)
        frame = camera.get_frame()
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
servostream = ""

################################
# Flask set up
################################
from flask import Flask, render_template  # as we are NOT using sudo must use a non-80 HTTP port
from flask import request
from flask import Response

from robot_camera_usb_opencv import Camera   # import the non-annotate custom openCV USB camera class

RPi_flex_app01 = Flask(__name__)  # creates a Flask object called RPi_flex_app01 for the web server operation


try:        

    # for this simple test code the following very large while-loop is just continuously running
    print("USBcamtest01.py: start continuous loop")
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
            select_mode = "selection routine",
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
            return Response(gen(Camera(pixwidth, pixheight)), mimetype='multipart/x-mixed-replace; boundary=frame')

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

