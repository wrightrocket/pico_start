from machine import Pin, ADC
from time import sleep

adc = ADC(Pin(26))


while True:
    duty = adc.read_u16()
    print(duty)
    sleep(1)