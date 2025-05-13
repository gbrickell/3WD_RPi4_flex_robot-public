#!/usr/bin/python

# file name: robot_camera_usb_opencv.py
# Robot camera openCV camera class: python code as part of a Flask based web server system
# version that is run using either 'sudo' or not, and DOES now use a ram drive 
#
# This class is used to create an instance of a USB camera managed by openCV with python code
#  and is used as part of the USBcamtest01.py and several different robot Flask controllers
#

import cv2     # import the python openCV library
import time    # import the required time functions
 
class Camera():

    # Constructor... build the new camera object with __init__ and additional width & height attributes
    def __init__(self, width, height):
        self.width = width
        self.height = height
        global stop_streaming

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
        time.sleep(0.2)  # wait another couple of seconds to make sure the camera is ready
        print ("Resolution set to " + str(self.width) + "x" + str(self.height) + " ...")

        # Prepare Capture: VideoCapture::read returns a true/false plus the next video frame or null
        self.ret, self.frame = self.cap.read()

    # Function for creating an image from camera frame for browser streaming with Flask...	
    def get_frame(self):
        global stop_streaming
        frame_state = "not set"
        # open a .jpg file to write in binary in the special ramdrive folder
        #   which has to have been set up previously by editing  /etc/fstab
        self.frames = open("/mnt/robot_ramimage/stream.jpg", 'wb+') 

        s, img = self.cap.read()   # get the next frame from the camera
        if s:	# check frame captures without errors...
            cv2.imwrite("/mnt/robot_ramimage/stream.jpg", img)	# Save image to the 'opened' .jpg  ...
            frame_state = "OK"
        else:
            # display an error message on screen if a next frame has not been grabbed
            if frame_state != "not set" and frame_state != "error":
                print (frame_state + ": frame capture at: " + time.strftime('%H:%M %Z'))
                frame_state = "error"
                stop_streaming = True
                self.cap.release()
        return self.frames.read()  # return the grabbed frame as the image


