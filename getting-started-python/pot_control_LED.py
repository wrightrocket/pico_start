from machine import Pin, PWM, ADC
from time import sleep

pwm = PWM(Pin(15))
adc = ADC(Pin(26))

pwm.freq(1000)

while True:
    duty = adc.read_u16()
    pwm.duty_u16(duty)
    print(duty)
    sleep(1)