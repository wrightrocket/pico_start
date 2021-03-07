from machine import Pin
from time import sleep

led_off_board = Pin(16, Pin.OUT)
button = Pin(15, Pin.IN, Pin.PULL_DOWN)
while True:
    if button.value():
        led_off_board.toggle()
        sleep(0.2)
        
