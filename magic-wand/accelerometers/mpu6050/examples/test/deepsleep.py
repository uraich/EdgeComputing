# Testing deep sleep mode
# Copyright (c) U. Raich

from machine import deepsleep
from machine import Pin
from utime import usleep
led = Pin(19,Pin.OUT)

# blink LED
led.value(~led.value())
sleep_my(500)
led.value(~led.value())
sleep_ms(500)

# wait 5 seconds so that you can catch the ESP awake to establish a serial communication later
# you should remove this sleep line in your final script
sleep(5)

print('Im awake, but Im going to sleep')

#sleep for 10 seconds (10000 milliseconds)
deepsleep(10000)
