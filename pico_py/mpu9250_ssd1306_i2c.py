''' Demonstrate MPU9500

Simple endless loop
'''
import utime
from machine import I2C, Pin
from mpu9250 import MPU9250
from ssd1306 import SSD1306_I2C

def dof9_init():
    SDA0 = Pin(8) # GPI0 8 is Pin 11
    SCL0 = Pin(9 )# GPIO 9 is Pin 12
    i2c0 = I2C(0, scl=SCL0, sda=SDA0)
    dof9 = MPU9250(i2c0)
    print("MPU9250 id: {}".format(hex(dof9.whoami)))
    return dof9
    
def dof9_calibrate():
    SDA0 = Pin(8) # GPI0 8 is Pin 11
    SCL0 = Pin(9 )# GPIO 9 is Pin 12
    i2c0 = I2C(0, scl=SCL0, sda=SDA0)
    dummy = MPU9250(i2c) # this opens the bybass to access to the AK8963
    ak8963 = AK8963(i2c)
    offset, scale = ak8963.calibrate(count=256, delay=200)
    
def oled_init():
    SDA1=Pin(26)
    SCL1=Pin(27)
    WIDTH  = 128                                            # oled display width
    HEIGHT = 64                                             # oled display height
    i2c1=I2C(1, sda=SDA1, scl=SCL1)
    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c1)
    print("SSD1306_I2C: {}".format(SSD1306_I2C))
    return oled

def data_display():
    while True:
        accel = "A {:.1f} {:.1f} {:.1f}".format(*dof9.acceleration)
        gyro = "G {:.1f} {:.1f} {:.1f}".format(*dof9.gyro)
        mag = "M {: .0f} {: .0f} {: .0f}".format(*dof9.magnetic)
        temp = "Celcius: {:.1f}".format(dof9.temperature)
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
        oled.show()

        utime.sleep_ms(1000)

if __name__ == '__main__':
    dof9 = dof9_init()
    oled = oled_init()
    data_display()