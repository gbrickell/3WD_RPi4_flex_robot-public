#!/usr/bin/python
#
# version for RPi-flex_PCB 3WD robot
# OLED_test01.py - simple I2C OLED test routine
#
# command:  python3 /home/pi3wdrobot/OLED_test/OLED_test01.py
#

####################################################################
###   function to clear the OLED screen AND the previous image   ###
####################################################################
def clearOLED(w, h):
    draw.rectangle((0,0,w,h), outline=0, fill=0)
    disp.clear()
    disp.display()
    return()

########################################################
###   function to display text on the OLED screen    ###
########################################################
def OLED_4lines(lin1, lin2, lin3, lin4, screentop, displayfont, dispimage):
    # lin1 to lin4 are text strings where the font is usually Lato-Regular.ttf size 15 or 16

    # Write four lines of text onto the image: need to adjust the 'spacing' for the font size
    # if font size is 15 or 16 the maximum #lines is 4 for the 128 x 64 display
    draw.text((x, top),    lin1,  font=displayfont, fill=255)
    draw.text((x, top+16), lin2,  font=displayfont, fill=255)
    draw.text((x, top+32), lin3,  font=displayfont, fill=255)
    draw.text((x, top+48), lin4,  font=displayfont, fill=255)

    # Display the image.
    disp.image(dispimage)  # set the buffer to the values of the Python Imaging Library (PIL) image
                           # the image should be in 1 bit mode and a size equal to the display size.
    disp.display()         # write the display buffer to the physical display

    return()


#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# main code 
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

import time # Import the Time library
import datetime

###################################
# 128x64 display with hardware I2C:
###################################
import Adafruit_SSD1306  # this is the set of software functions for the display hardware that has to have been previously 'installed'
# import the standard Python Image Library (PIL) modules to draw images
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

RST = None     # on the Pi OLED this pin is not used
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)   # default OLED display i2c_address=0x3C

# Note you can change the I2C address by passing an i2c_address parameter like:
#   disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)

# Alternatively you can specify an explicit I2C bus number, for example
# with the 128x32 display you would use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=2)
# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Use a drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# First define some constants to allow easy resizing of what is put to the display.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font - need to use the full path to any designated font other than the default
# note the default font is quite small (size 8) 
# font = ImageFont.load_default()

# should be able to use any of the fonts that are usually installed at /usr/share/fonts/
# example using /usr/share/fonts/truetype/lato/Lato-Regular.ttf
font = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Regular.ttf', 16)  # using font size 16

#----------------------------------------------------------------------------
try:
    # create and show start-up text
    clearOLED(width, height)
    line1 = "* system starting *"
    line2 = " "
    line3 = " "
    line4 = " "
    print ("displaying the system starting text")
    clearOLED(width, height)
    OLED_4lines(line1, line2, line3, line4, top, font, image)
    time.sleep(15)   # short pause so that this display stays on a while
    clearOLED(width, height)
except KeyboardInterrupt:
    clearOLED(width, height)

