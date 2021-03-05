from machine import Pin, PWM, ADC
from time import sleep


adc = ADC(Pin(26)) #Pin.IN
dataReadyPin = Pin(16, Pin.OUT)

PRESSURE_LSB = 0x20
TEMPERATURE = 0x21
sensorValue = 0
count = 50000.0

while True:
    #duty = adc.read_u16()
    #print(duty)
    #sleep(1)
    
    for x in range(count):
        sensorValue += adc.read_u16() # //Add analog values of sensor 500 times 
    sensorValue = sensorValue/count# //Take average of readings
    sensor_volt = sensorValue*(5.0/1023.0)# //Convert average to voltage 
    # RS_air = ((5.0*10.0)/sensor_volt)-10.0# //Calculate RS in fresh air
    RS_air = ((5.0*10.0)/sensor_volt)# //Calculate RS in fresh air 
    R0 = RS_air/4.4# //Calculate R0 
    print("RS_air = ", RS_air, "R0 = ", R0)# //Display "R0"
