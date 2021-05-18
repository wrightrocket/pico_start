"""
Exercise on Raspberry Pi Pico/MicroPython
with 320x240 ILI9341 SPI Display
"""
from ili934xnew import ILI9341, color565
from machine import Pin, SPI
from micropython import const
import os
import glcdfont
import tt14
import tt24
import tt32
import utime

import freesans48
import freesans48fixed

SCR_WIDTH = const(320)
SCR_HEIGHT = const(240)
SCR_ROT = const(1)   #const(2)
CENTER_Y = int(SCR_WIDTH/2)
CENTER_X = int(SCR_HEIGHT/2)

print(os.uname())
TFT_CLK_PIN = const(10)
TFT_MOSI_PIN = const(11)
TFT_MISO_PIN = const(12)

TFT_CS_PIN = const(13)
TFT_RST_PIN = const(14)
TFT_DC_PIN = const(15)


spi = SPI(
    1,
    baudrate=40000000,
    miso=Pin(TFT_MISO_PIN),
    mosi=Pin(TFT_MOSI_PIN),
    sck=Pin(TFT_CLK_PIN))
print(spi)

display = ILI9341(
    spi,
    cs=Pin(TFT_CS_PIN),
    dc=Pin(TFT_DC_PIN),
    rst=Pin(TFT_RST_PIN),
    w=SCR_WIDTH,
    h=SCR_HEIGHT,
    r=SCR_ROT)

display.erase()
display.set_pos(0,0)

#demo freesans48
display.set_font(freesans48)
display.erase()
display.set_pos(0,0)
display.print("freesans48")
display.print("1234567890")
utime.sleep(1)
    
display.erase()
display.set_pos(0,0)
display.print("ABCDEFGHIJKLMNOPQRST")
utime.sleep(1)
display.erase()
display.set_pos(0,0)
display.print("UVWXYZ")
utime.sleep(1)
display.erase()
display.set_pos(0,0)
display.print("abcdefghijklmno")
utime.sleep(1)
display.erase()
display.set_pos(0,0)
display.print("pqrstuvwxyz")
utime.sleep(1) 

#demo freesans48fixed
display.erase()
display.set_pos(0,0)

display.set_font(freesans48fixed)

display.print("freesans48fixed")

utime.sleep(1)


for i in range(130):
    display.scroll(1)
    utime.sleep(0.01)
utime.sleep(1)
for i in range(130):
    display.scroll(-1)
    utime.sleep(0.01)
utime.sleep(1)


display.erase()
display.set_pos(0,0)
display.print("ABCDEFGHIJKLMNOPQ")
utime.sleep(1)
display.erase()
display.set_pos(0,0)
display.print("RSTUVWXYZ")
utime.sleep(1)
display.erase()
display.set_pos(0,0)
display.print("abcdefghijklmno")
utime.sleep(1)
display.erase()
display.set_pos(0,0)
display.print("pqrstuvwxyz")
utime.sleep(1)

display.erase()
display.set_pos(0,0)
display.print("1234567890")
utime.sleep(1)
display.erase()
display.set_pos(0,0)
display.print("!@#$%^&*()~_`-")
utime.sleep(1)
display.erase()
display.set_pos(0,0)
display.print("{}[]:;<>,.?/|")
utime.sleep(1)

print("- bye-")
