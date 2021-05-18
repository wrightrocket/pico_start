import machine
import bmp280 
SDA=machine.Pin(26)
SCL=machine.Pin(27)
bus=machine.I2C(1, sda=SDA, scl=SCL)

# bus=machine.I2C(0)
bmp = bmp280.BMP280(bus, addr=0x77)
print(bmp.temperature)
print(bmp.pressure)