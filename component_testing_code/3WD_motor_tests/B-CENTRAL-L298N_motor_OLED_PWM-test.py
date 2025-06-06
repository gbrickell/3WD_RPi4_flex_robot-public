#!/usr/bin/python
# Back central motor testing
# B-CENTRAL motor uses the rear L298N controller - pins: enB, IN3, IN4
# omni wheeel PCB version of L298N single motor test
# using a L298N to control the motor with PWM

# command to run:  python3 /home/pi3wdrobot/motor_tests_3WD_versions/B-CENTRAL-L298N_motor_OLED_PWM-test.py

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
# Raspberry Pi L298N more developed PWM motor functions but based upon the article at 
#  https://www.instructables.com/id/Control-DC-and-stepper-motors-with-L298N-Dual-Moto/
#  which describes the L298N motor controller use with an Arduino Uno
# 
#  N.B. depending upon how the motors are connected the motor direction
#    signals to the in1, in2, in3 and in4 pins may need to be reversed
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

########################################################################################
def Rb_motor_pwm(Rin3, Rin4, dutycycle):  # allows the rear (R) L298N 'b' motor e.g. for mecanum wheels to be controlled
    # assumes pwm_RenB has beRenB set up in the main code
    dutycycle = int(dutycycle) # force as an integer just in case 
    Rin3 = int(Rin3)           # force as an integer just in case
    Rin4 = int(Rin4)           # force as an integer just in case
    # individual motor control with a +'ve or -'ve dutycycle to set the motor forwards or backwards
    if dutycycle == 0:   # stop the motor using the 'hard' brake method
        # motor braking
        # set RenB with 100% PWM dutycycle
        pwm_RenB.start(100)
        # set Rin3 off and Rin4 off i.e. LOW- LOW for no motion
        GPIO.output(Rin3, 0)
        GPIO.output(Rin4, 0)
    elif dutycycle > 0:  # move forwards
        # set RenB with the PWM dutycycle
        pwm_RenB.start(dutycycle)
        # set Rin3 off and Rin4 on i.e. HIGH - LOW for forward motion
        GPIO.output(Rin3, 1)
        GPIO.output(Rin4, 0)
    elif dutycycle < 0:  # move backwards
        # set RenB with the PWM dutycycle
        pwm_RenB.start(abs(dutycycle))
        # set Rin3 on and Rin4 off i.e. LOW - HIGH for backward motion
        GPIO.output(Rin3, 0)
        GPIO.output(Rin4, 1)


#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# main code
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

import RPi.GPIO as GPIO # Import the GPIO Library
import time # Import the Time library

###################################
# 128x64 display with hardware I2C:
###################################
# this is the set of software functions for the display hardware that has to have beRenB previously 'installed'
import Adafruit_SSD1306  
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
# Move left to right keeping track of the currRenBt x position for drawing shapes.
x = 0

# Load default font - need to use the full path to any designated font other than the default
# note the default font is quite small (size 8) 
# font = ImageFont.load_default()

# should be able to use any of the fonts that are usually installed at /usr/share/fonts/
# example using /usr/share/fonts/truetype/lato/Lato-Regular.ttf
font = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Regular.ttf', 16)  # using font size 16

#---------------------------------------------------------------------------
# create and show start-up text
clearOLED(width, height)
line1 = "* system starting *"
line2 = "**** B-CENTRAL ****"
line3 = " "
line4 = " "
print ("displaying the system starting text")
clearOLED(width, height)
OLED_4lines(line1, line2, line3, line4, top, font, image)
time.sleep(2)   # short pause so that this display stays on a while

# Set the GPIO modes
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# L298N setup code
# FL motor uses the rear L298N controller - pins: enB, IN3, IN4
# the rear L298N uses the 'outboard' 6P connector on the PCB
RenB = 24   # this will be a software set PWM pin
Rin3 = 8
Rin4 = 25

# Set the GPIO Pin mode
GPIO.setup(RenB, GPIO.OUT)
GPIO.setup(Rin3, GPIO.OUT)
GPIO.setup(Rin4, GPIO.OUT)

# set the various PWM parameters
# How many times to turn the GPIO pin on and off each second 
Frequency = 20      # usually 20
# How long the GPIO pin stays on each cycle, as a percRenBt  
# Setting the duty cycle to 0 means the motors will not turn
DutyCycle = 50     # usually 30 for a quite slow turn rate
Stop = 0

pwm_RenB = GPIO.PWM(RenB, Frequency)  # set the RenBA pin as a software set PWM pin
# Start the software PWM pins with a duty cycle of 0 (i.e. motors not moving)
pwm_RenB.start(0)

# Turn motor off - hard brake
Rb_motor_pwm(Rin3, Rin4, 0)
line1 = "Driving motor:"
line2 = "motor off"
line3 = " "
line4 = " "
print ("displaying motor stopped")
clearOLED(width, height)
OLED_4lines(line1, line2, line3, line4, top, font, image)
time.sleep(1)

# run tests
try:
    # motor forward 100%
    Rb_motor_pwm(Rin3, Rin4, 100)
    line1 = "Driving motor:"
    line2 = "motor anticlock"
    line3 = "speed 100%"
    line4 = " "
    print ("displaying motor drive shaft rotating anticlock wise")
    clearOLED(width, height)
    OLED_4lines(line1, line2, line3, line4, top, font, image)
    time.sleep(4)

    # motor forward 60%
    Rb_motor_pwm(Rin3, Rin4, 60)
    line1 = "Driving motor:"
    line2 = "motor anticlock"
    line3 = "speed 60%"
    line4 = " "
    print ("displaying motor drive shaft rotating anticlock wise")
    clearOLED(width, height)
    OLED_4lines(line1, line2, line3, line4, top, font, image)
    time.sleep(4)

    # Turn motor off - hard brake
    Rb_motor_pwm(Rin3, Rin4, 0)
    line1 = "Driving motor:"
    line2 = "motor off"
    line3 = " "
    line4 = " "
    print ("displaying motor stopped")
    clearOLED(width, height)
    OLED_4lines(line1, line2, line3, line4, top, font, image)

    # motors clockwise 100%
    Rb_motor_pwm(Rin3, Rin4, -100)
    line1 = "Driving motor:"
    line2 = "motor clockwise"
    line3 = "speed 100% "
    line4 = " "
    print ("displaying motor drive shaft rotating clockwise")
    clearOLED(width, height)
    OLED_4lines(line1, line2, line3, line4, top, font, image)
    time.sleep(4)

    # motors clockwise 60%
    Rb_motor_pwm(Rin3, Rin4, -60)
    line1 = "Driving motor:"
    line2 = "motor clockwise"
    line3 = "speed 60% "
    line4 = " "
    print ("displaying motor drive shaft rotating clockwise")
    clearOLED(width, height)
    OLED_4lines(line1, line2, line3, line4, top, font, image)
    time.sleep(4)

    # Turn motor off - hard brake
    Rb_motor_pwm(Rin3, Rin4, 0)
    line1 = "Driving motor:"
    line2 = "motor off"
    line3 = " "
    line4 = " "
    print ("displaying motor stopped")
    clearOLED(width, height)
    OLED_4lines(line1, line2, line3, line4, top, font, image)

    line1 = "Program ended"
    line2 = " "
    line3 = " "
    line4 = " "
    print ("program ended")
    clearOLED(width, height)
    OLED_4lines(line1, line2, line3, line4, top, font, image)
    GPIO.cleanup()
    time.sleep(5)
    clearOLED(width, height)

except KeyboardInterrupt:
    # Turn motor off - hard brake
    Rb_motor_pwm(Rin3, Rin4, 0)
    clearOLED(width, height)
