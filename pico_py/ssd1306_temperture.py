from machine import ADC
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf
from time import sleep

WIDTH  = 128                                            # oled display width
HEIGHT = 64                                             # oled display height
TEMP_ADC = 4
SDA = 8 # GPI0 8 is Pin 11
SCL = 9 # GPIO 9 is Pin 12
i2c = I2C(0, scl=Pin(SCL), sda=Pin(SDA), freq=200000)       # Init I2C using pins GP8 & GP9 (default I2C0 pins)
print("I2C Address      : "+hex(i2c.scan()[0]).upper()) # Display device address
print("I2C Configuration: "+str(i2c))                   # Display I2C config


oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)                  # Init oled display

# Raspberry Pi logo as 32x32 bytearray
buffer = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|?\x00\x01\x86@\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00~\xfc\x00\x00L'\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c \x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

# Load the raspberry pi logo into the framebuffer (the image is 32x32)
fb = framebuf.FrameBuffer(buffer, 32, 32, framebuf.MONO_HLSB)

# Clear the oled display in case it has junk on it.
oled.fill(0)

# Blit the image from the framebuffer to the oled display
oled.blit(fb, 96, 0)

# Add some text
oled.text("Raspberry Pi",5,5)
oled.text("Pico",5,15)

# Finally update the oled display so the image & text is displayed
oled.show()

while True:
    sleep(5)
    temp_sensor = ADC(TEMP_ADC)
    temperature = temp_sensor.read_u16()
    to_volts = 3.3 / 65535
    temperature = temperature * to_volts
    celsius_degrees = 27 - (temperature - 0.706) / 0.001721
    fahrenheit_degrees = celsius_degrees * 9 / 5 + 32
    print(fahrenheit_degrees)
    oled.fill(0)

# Blit the image from the framebuffer to the oled display
    oled.blit(fb, 96, 0)
    oled.text(str(fahrenheit_degrees),5,5)
