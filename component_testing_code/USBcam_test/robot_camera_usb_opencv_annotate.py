#!/usr/bin/python

# file name: robot_camera_usb_opencv_annotate.py
# Robot camera openCV camera class: python code as part of a Flask based web server system
# version that is run using the 'user' (i.e. non-sudo) version of the app and DOES now use a ram drive 
#  - this version also annotates the image using the convert (imagemagick) function
#  - this version also includes an annotated 'distance' value from the ultrasonic sensor with a servo position
#
# This class is used to create an instance of a USB camera managed by openCV with python code
#  and is used as part of several overall robot controllers which includes Flask for web access
#

global pinTrigger
global pinEcho

import cv2     # import the python openCV library
import time    # import the required time functions
import os

################################
# allow C libraries to be used
################################
from ctypes import *
debug = 0   # outputs more info to the screen: set to 0 once code is in production use
# for GPIO functions the custom C library is used which uses the wiringPi functions
flexbot02_gpio = CDLL("/home/pi3wdrobot/RPi-flex_pi_PCB_robot/libRPiflex03_gpio.so")
# set the Broadcom pin numbering
flexbot02_gpio.set_broadcom(debug)
flexbot02_gpio.connect()  # check that the 'C' library has been found

################################
# GPIO set up
################################
pinTrigger =  27
pinEcho =  22

# set the Trigger and Echo pins as OUTPUT and INPUT respectively
flexbot02_gpio.setIO_GPIO(pinTrigger, 1)   # Trigger 
flexbot02_gpio.setIO_GPIO(pinEcho, 0)      # Echo

#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# individual ultrasonic sensor control functions - using 'C'
#   special variant version for the USB camera 'annotate' functions
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# Take a distance measurement - this version is customised for the USB camera streaming code
def Measure(): 
    global pinTrigger
    global pinEcho
    # set the Trigger LOW for a period 
    flexbot02_gpio.setlow_ultra(pinTrigger, 100000, debug) # 100 ms settling period
    # send a 10us HIGH to trigger the sensor's ranging program (which sends 8 ultrasound bursts at 40 kHz)
    flexbot02_gpio.send_ultra(pinTrigger, 10, debug)

    # Start the timer
    InitTime = time.time()
    StartTime = time.time() 
    StopTime = StartTime
    tooshort = "no"
    abort1 = "no"
    abort2 = "no"

    # The start time is reset until the Echo pin is taken high (==1)
    while flexbot02_gpio.read_pin(pinEcho)==0: 
        StartTime = time.time() 
        StopTime = StartTime
        if StartTime-InitTime > 3.0: # taking too long to capture 1st timestamp
            print ("Taking too long to capture 1st timestamp aborting measurement")
            abort1 = "yes1"
            Distance = 0.0
            diststream = str(Distance)
            return (Distance, tooshort, abort1)

    # Stop when the Echo pin is no longer high - the end time
    while flexbot02_gpio.read_pin(pinEcho)==1:  
        StopTime = time.time() 
        # If the sensor is too close to an object, the Pi cannot 
        # see the echo quickly enough, so it misses the response and waits and 
        # waits setting a 'trip' time that is unrealistically long so the code can  
        # detect the missed signal problem and say what has happened 
        if StopTime-StartTime >= 0.04:   # a time of 0.04 implies >6.8m !
            print("Hold on there! Return pulse missed or you're too close.") 
            abort2 = "yes2"
            tooshort = "yes"
            Distance = 0.0
            diststream = str(Distance)
            return (Distance, tooshort, abort2)

    ElapsedTime = StopTime - StartTime    # Calculate pulse length
    Distance = (ElapsedTime * 34326)/2    # speed of sound in air is 343.26 m/s so distance is in cm
    diststream = str(round(Distance,2))
    #print ("Distance: " + diststream )
    return (diststream, tooshort, abort2)

#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 
class Camera():

    # Constructor... build the new camera object with __init__ and additional width & height attributes
    def __init__(self, width, height):
        self.width = width
        self.height = height
        global stop_streaming
        global servostream
        global textpos1
        global textpos2
        global blackrectangle
        global servotext
        global objecttext
        global aborttext

        # use the openCV VideoCapture class
        self.cap = cv2.VideoCapture(-1)  # Prepare the camera... using -1 selects the first working camera
        cap_count = 0
        while(self.cap.isOpened() != True):
            print("Camera warming up ...")
            time.sleep(1)  # wait a second to make sure the camera is ready
            cap_count = cap_count + 1
            if cap_count > 3:   # check if camera is not coming up
                print("Camera not restarting - try to stop streaming")
                stop_streaming = True
                self.cap.release()
                break

        # use openCV VideoCapture::set to set both the width and height camera parameters
        self.cap.set(3, self.width)
        self.cap.set(4, self.height)
        time.sleep(0.1)  # wait a short period to make sure the camera is ready

        # set the text positioning for the annotation on the image - done once here in the _init_ code to the 'global' variables
        if str(self.width) == "640":
            textpos2 = "+410+465"
            textpos1 = "+15+465"
            blackrectangle = "rectangle\ 640,452\ 0,470"
            servotext = "servo:\ "
            objecttext = "object\ distance:\ "
            aborttext = "aborted\ measurement"
        elif str(self.width) == "320":
            textpos2 = "+180+225"
            textpos1 = "+10+225"
            blackrectangle = "rectangle\ 320,212\ 0,230"
            servotext = "servo:\ "
            objecttext = "object:\ "
            aborttext = "aborted\ measurement"
        elif str(self.width) == "160":
            textpos2 = "+92+105"
            textpos1 = "+3+105"
            blackrectangle = "rectangle\ 160,93\ 0,110"
            servotext = "s:\ "
            objecttext = ""
            aborttext = "aborted"
        print ("Resolution set to " + str(self.width) + "x" + str(self.height) + " ...")

        # Prepare Capture: VideoCapture::read returns a true/false plus the next video frame or null
        self.ret, self.frame = self.cap.read()

    # Function for creating an image from camera frame for browser streaming with Flask...	
    def get_frame(self, servostream):
        global stop_streaming
        global textpos1
        global textpos2
        global blackrectangle
        global servotext
        global objecttext

        self.servostream = servostream

        frame_state = "not set"
        # open a .jpg file to write in binary in the special ramdrive folder
        #   which has to have been set up previously by editing  /etc/fstab
        filename = "/mnt/robot_ramimage/stream.jpg"
        self.frames = open(filename, 'wb+')

        s, img = self.cap.read()   # get the next frame from the camera
        if s:	# check frame captures without errors...
            #print("next image found")
            cv2.imwrite(filename, img)	# Save image to the 'opened' .jpg  ...
            # create a black filled area for overlaying the annotation text in white
            os_image_command0 = "convert " + filename + " -fill black -draw " + blackrectangle + " " + filename
            os.system(os_image_command0) # execute command0
            # construct commands to 'annotate' the image file
            annotation1 = servotext + self.servostream + "deg"  # escaped spaces so they do not 'trigger' the next parameter in the convert command
            Distance, tooshort, abort = Measure()
            #print ("Distance, tooshort, abort: " + str(Distance) + " - "  + str(tooshort) + " - " + str(abort))
            if str(abort) == "yes1" or str(abort) == "yes2"  or str(tooshort) == "yes" :
                annotation2 = aborttext
            else:
                annotation2 = objecttext + str(Distance) + "\ cm"   # escaped spaces so they do not 'trigger' the next parameter in the convert command
            os_image_command1 = "convert " + filename + " -font Courier -pointsize 14 -fill white -annotate " + textpos1 + " " + annotation1 + " " + filename
            os.system(os_image_command1) # execute command1
            #print("annotate 1 command completed:" + annotation1)
            os_image_command2 = "convert " + filename + " -font Courier -pointsize 14 -fill white -annotate " + textpos2 + " " + annotation2 + " " + filename
            os.system(os_image_command2) # execute command2
            #print("annotate 2 command completed")
            frame_state = "OK"
        else:
            # display an error message on screen if a next frame has not been grabbed
            if frame_state != "not set" and frame_state != "error":
                print (frame_state + ": frame capture at: " + time.strftime('%H:%M %Z'))
                frame_state = "error"
                stop_streaming = True
                self.cap.release()
        return self.frames.read()  # return the grabbed frame as the image


