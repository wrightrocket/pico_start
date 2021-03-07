from machine import Pin
from time import sleep

led_on_board = Pin(25, Pin.OUT)
led_off_board = Pin(15, Pin.OUT)
i = 0
while True:
    i += 1
    if i % 2 == 0:
        led_on_board.on()
        led_off_board.off() 
    else:
        led_on_board.off()
        led_off_board.on() 
    sleep(0.33)
