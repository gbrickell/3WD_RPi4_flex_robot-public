#!/usr/bin/python
# 
# version for RPi-flex_PCB 3WD robot
# command to run:  python3 /home/pi3wdrobot/ultrasonic_sensor/sensor-distance.py

import RPi.GPIO as GPIO # Import the GPIO Library
import time # Import the Time library

# Set the GPIO modes
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define GPIO pins to use on the Pi
# as per the RPi Maker Kit
pinTrigger = 27
pinEcho = 22

print("Ultrasonic Measurement")

# Set pins as output and input
GPIO.setup(pinTrigger, GPIO.OUT)  # Trigger
GPIO.setup(pinEcho, GPIO.IN)      # Echo

print ("GPIO pins configured - strting measurements")

try:
    # Repeat the next indented block forever
    while True:
        # Set trigger to False (Low)
        GPIO.output(pinTrigger, False)

        # Allow module to settle
        time.sleep(0.5)

        # Send 10us pulse to trigger
        GPIO.output(pinTrigger, True)
        time.sleep(0.00001)
        GPIO.output(pinTrigger, False)

        # Start the timer
        StartTime = time.time()

        # The start time is reset until the Echo pin is taken high (==1)
        while GPIO.input(pinEcho)==0:
            StartTime = time.time()

        # Stop when the Echo pin is no longer high - the end time
        while GPIO.input(pinEcho)==1:
            StopTime = time.time()
            # If the sensor is too close to an object, the Pi cannot
            # see the echo quickly enough, so we have to detect that
            # problem and say what has happened.
            if StopTime-StartTime >= 0.04:
                print("Hold on there!  You're too close for me to see.")
                StopTime = StartTime
                break

        # Calculate pulse length
        ElapsedTime = StopTime - StartTime

        # Distance pulse travelled in that time is
        # time multiplied by the speed of sound (cm/s)
        Distance = ElapsedTime * 34326

        # That was the distance there and back so halve the value
        Distance = Distance / 2

        print("Distance: %.1f cm" % Distance)

        time.sleep(0.5)

# If you press CTRL+C, cleanup and stop
except KeyboardInterrupt:
    # Reset GPIO settings
    GPIO.cleanup()
