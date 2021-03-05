from machine import ADC
from machine import Pin, I2C
# from ssd1306 import SSD1306_I2C
import framebuf
import rp2
import ds18x20
import onewire

WIDTH  = 128                                            # oled display width
HEIGHT = 32                                             # oled display height

SDA = 8
SCL = 9
i2c = I2C(0, scl=Pin(SCL), sda=Pin(SDA))       # Init I2C using pins GP8 & GP9 (default I2C0 pins)
print("I2C Address      : "+hex(i2c.scan()[0]).upper()) # Display device address
print("I2C Configuration: "+str(i2c))                   # Display I2C config
'''
__main__          gc                uasyncio/event    ujson
_boot             machine           uasyncio/funcs    uos
_onewire          math              uasyncio/lock     urandom
_rp2              micropython       uasyncio/stream   ure
_thread           onewire           ubinascii         uselect
_uasyncio         rp2               ucollections      ustruct
builtins          uarray            uctypes           usys
ds18x20           uasyncio/__init__ uhashlib          utime
framebuf          uasyncio/core     uio               uzlib
Plus any modules on the filesystem
'''
help('modules')
import machine
help(machine)