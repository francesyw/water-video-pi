#
# Author:      Frances Yuan Wang
# Description: Connecting water flow sensors with Raspberry Pi GPIO
#              and use it to control the playback of the videos
#

import RPi.GPIO as GPIO
from omxplayer import OMXPlayer
import time
import threading

pin_a = 17
pin_b = 23
input_state_a = 0
input_state_b = 0
window_size = 0.8
window_start = time.time()
window_end = int(window_start) + window_size
sensor_state_a = False
last_sensor_state_a = False
sensor_state_b = False
last_sensor_state_b = False
pulses_a = 0
pulses_b = 0
threshold = 18

movie = ("/home/pi/project/test.mp4")
head1 = 0
head2 = 31.0
pos1 = 0
pos2 = 30.0
isClip1 = True
last_state_clip = True
player = OMXPlayer(movie, args=['--no-osd', '-b'])
movie_duration = player.duration() - 0.3

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)

player.pause()
player.set_position(head1)
player.play()
print "video 1 playing"
# print player.position()

def debug():
    t =  threading.Timer(1.0, debug)
    t.daemon = True
    t.start()
    print ("pulses_b: ", pulses_b, " | sensor b: ", sensor_state_b)

# debug()

def play_control(pos):
    player.pause()
    player.set_position(pos)
    player.play()
    print ("video position: ", player.position())

try:
    while True:
        # Read states of inputs
        input_state_a = GPIO.input(pin_a)
        input_state_b = GPIO.input(pin_b)
        # print ("pin a: ", input_state_a)

        # loop the clips
        if isClip1 and player.position() >= 29.9:
           play_control(head1)
        elif not isClip1 and player.position() > movie_duration:
           play_control(head2)

        # count pulses within a window frame and determaine the sensor states
        if window_end < time.time():
            # print ("pin 17 pulses: ", pulses_a)
            sensor_state_a = True if (pulses_a > threshold) else False
            sensor_state_b = True if (pulses_b > threshold) else False
            # print ("sensor a: ", sensor_state_a)

            # If GPIO(17 or 23) state has changed
            if (sensor_state_a is not last_sensor_state_a) or (sensor_state_b is not last_sensor_state_b):
                print "Pin states changed."

                # if both of the sensors are "off", play video a
                if not sensor_state_a and not sensor_state_b:
                    isClip1 = True
                    if isClip1 is not last_state_clip:
                        pos2 = player.position()
                        play_control(pos1)
                else:
                    # any of the sensors are "on", play video b
                    isClip1 = False
                    if isClip1 is not last_state_clip:
                        pos1 = player.position()
                        play_control(pos2)

            last_state_clip = isClip1
            last_sensor_state_a = sensor_state_a
            last_sensor_state_b = sensor_state_b
            pulses_a = 0
            pulses_b = 0
            window_end += window_size
        else:
            if not input_state_a:
                pulses_a += 1
            if not input_state_b:
                pulses_b += 1

except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    player.quit()
    GPIO.cleanup() # cleanup all GPIO
    print "all cleaned"

