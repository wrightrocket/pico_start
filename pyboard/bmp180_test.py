from machine import Pin, I2C
from bmp180 import BMP180
# SDA1=Pin(21)
# SCL1=Pin(20)
# bus=I2C(1, sda=SDA1, scl=SCL1)
bus = I2C(0)
bmp = BMP180(bus)

print("Temp C:", bmp.temperature)
print("Pressure: ", bmp.pressure)
print("Altitude: ", bmp.altitude)