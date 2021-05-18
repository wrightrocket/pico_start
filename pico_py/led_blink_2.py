from machine import Pin
from time import sleep

led = Pin(25, Pin.OUT)
i = 0
while True:
    i += 1
    if i % 2 == 0:
        led.on()
    else:
        led.off()
    sleep(0.1)
    