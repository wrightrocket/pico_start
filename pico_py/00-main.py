from machine import Pin
from time import sleep

led = Pin(25, Pin.OUT)
for i in range(14):
    if i % 2 == 0:
        led.on()
    else:
        led.off()
    sleep(1)    
