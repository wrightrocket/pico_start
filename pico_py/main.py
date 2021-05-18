''' Demonstrate MPU9500

Simple endless loop
'''
import utime
from machine import I2C, Pin
from mpu9250 import MPU9250
from ssd1306 import SSD1306_I2C

SDA0 = Pin(8) # GPI0 8 is Pin 11
SCL0 = Pin(9 )# GPIO 9 is Pin 12
SDA1=Pin(26)
SCL1=Pin(27)
WIDTH  = 128                                            # oled display width
HEIGHT = 64                                             # oled display height

i2c0 = I2C(0, scl=SCL0, sda=SDA0)
sensor = MPU9250(i2c0)

i2c1=I2C(1, sda=SDA1, scl=SCL1)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c1)

print("MPU9250 id: " + hex(sensor.whoami))

while True:
    accel = "A {:.1f} {:.1f} {:.1f}".format(*sensor.acceleration)
    gyro = "G {:.1f} {:.1f} {:.1f}".format(*sensor.gyro)
    mag = "M {: .0f} {: .0f} {: .0f}".format(*sensor.magnetic)
    temp = "Celcius: {:.1f}".format(sensor.temperature)
    print(accel)
    print(gyro)
    print(mag)
    print(temp)
    print()
    
    oled.fill(0) # clear screen
    oled.text(accel, 5, 0)
    oled.text(gyro, 5, 16)
    oled.text(mag, 5, 32)
    oled.text(temp, 5, 48)
 
    #oled.text(str(c_degrees),5,10)
    oled.show()

    utime.sleep_ms(1000)