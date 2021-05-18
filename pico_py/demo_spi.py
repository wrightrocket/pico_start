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
import time

SCR_WIDTH = const(320)
SCR_HEIGHT = const(240)
SCR_ROT = const(2)
CENTER_Y = int(SCR_WIDTH/2)
CENTER_X = int(SCR_HEIGHT/2)

print(os.uname())
'''
TFT_CLK_PIN = const(10)
TFT_MOSI_PIN = const(11)
TFT_MISO_PIN = const(12)
TFT_CS_PIN = const(13)
TFT_RST_PIN = const(14)
TFT_DC_PIN = const(15)
'''
# TFT_CLK_PIN = Pin(10, Pin.OUT, Pin.PULL_UP)
TFT_CLK_PIN = Pin(10)
TFT_MOSI_PIN = Pin(11)
TFT_MISO_PIN = Pin(12)
TFT_CS_PIN = Pin(13, Pin.OUT, Pin.PULL_UP)
TFT_RST_PIN = Pin(14)
TFT_DC_PIN = Pin(15, Pin.OUT, Pin.PULL_UP)

fonts = [glcdfont,tt14,tt24,tt32]
text = 'Hello Raspberry Pi Pico/ili9341'

print(text)
print("fonts available:")
for f in fonts:
    print(f.__name__)

spi = SPI(
    1,
    baudrate=40000000,
    miso=TFT_MISO_PIN,
    mosi=TFT_MOSI_PIN,
    sck=TFT_CLK_PIN)
print(spi)

display = ILI9341(
    spi,
    cs=TFT_CS_PIN,
    dc=TFT_DC_PIN,
    rst=TFT_RST_PIN,
    w=SCR_WIDTH,
    h=SCR_HEIGHT,
    r=SCR_ROT)

print(dir(display))
display.reset()
display.erase()
display.set_pos(0,0)

for ff in fonts:
    display.set_font(ff)
    display.print(text)
    
display.set_font(tt24)
display.set_color(color565(255, 255, 0), color565(150, 150, 150))
display.print("\nThanks:")
display.print("https://github.com/jeffmer/micropython-ili9341")
print("\nThanks:")
print("https://github.com/jeffmer/micropython-ili9341")
time.sleep(1)
