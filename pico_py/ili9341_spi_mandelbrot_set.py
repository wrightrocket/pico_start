from machine import Pin, SPI, ADC
from ili934xnew import ILI9341, color565
import time
import math
import _thread

WIDTH=320
HEIGHT=240
ROTATION=1

#TFT pins are wired accordingly
TFT_CLK_PIN = const(10)
TFT_MOSI_PIN = const(11)
TFT_MISO_PIN = const(12)
TFT_CS_PIN = const(13)
TFT_RST_PIN = const(14)
TFT_DC_PIN = const(15)

def init_tft():
    spi = SPI(1,baudrate=40000000,miso=Pin(TFT_MISO_PIN),mosi=Pin(TFT_MOSI_PIN),sck=Pin(TFT_CLK_PIN))
    display = ILI9341(spi,cs=Pin(TFT_CS_PIN),dc=Pin(TFT_DC_PIN),rst=Pin(TFT_RST_PIN),w=WIDTH,h=HEIGHT,r=ROTATION)
    display.erase()
    return display
    
MAX_ITER = 80
def mandelbrot(c):
    z,n = 0,0
    while abs(z) <= 2 and n < MAX_ITER:
        z = z*z + c
        n += 1
    return n

xOffset = -0.8
RE_START = -2 + xOffset
RE_END = 2 + xOffset
IM_START = -1
IM_END = 1

ZOOM_IM = 1.2 #1=100% 0.5=200%
ZOOM_RE = 0.8 #1=100% 0.5=200%
OFFSET_IM = 0
OFFSET_RE = 0


BLACK = color565(0,0,0)   
WHITE = color565(255,255,255)
RED = color565(255,0,0)
GREEN = color565(0,255,0)
BLUE = color565(0,255,0)
YELLOW = color565(255,255,0)
CIAN = color565(0,255,255)
MAGENTA = color565(255,9,255)
colors = (WHITE,YELLOW,RED,GREEN,BLUE,CIAN,BLACK,MAGENTA)

building = False 
def buildFractal():
    global building
    global buf
    if building==True:
        return
    building=True
    display = init_tft();
    RE_START_OFF    = RE_START + OFFSET_RE
    RE_WIDTH        = RE_END - RE_START
    IM_START_OFF    = IM_START + OFFSET_IM
    IM_WIDTH        = IM_END - IM_START
    ticks_start = time.ticks_ms()
    for x in range(0, WIDTH):
        xx = (RE_START_OFF + (x / WIDTH) * RE_WIDTH) * ZOOM_RE
        for y in range(0, HEIGHT):
            yy = (IM_START_OFF + (y / HEIGHT) * IM_WIDTH) * ZOOM_IM
            c = complex(xx, yy) # Convert pixel coordinate to complex number
            m = mandelbrot(c)   # Compute the number of iterations
            colorIndex = int(m/11) #colors[m//12]
            if colorIndex > 0:
                display.pixel(x, y, colors[colorIndex]) # Plot the point
    print("Total Time={}!!!!!".format(time.ticks_diff(time.ticks_ms(), ticks_start)))
    building = False
      
display = init_tft();      

#button is used to start building Mandelbrot Set
button=Pin(9, Pin.IN, Pin.PULL_DOWN)

#3 potentiometers are used to parametrise zom, zoom pan x and pan y
#they are wired to ground and 3.3V and middle pin's voltage goes to
#ADC to get varing value into the pico.
zoom = ADC(28)
pan_x = ADC(27)
pan_y = ADC(26)
buildFractal()
while True:
    if button.value()==1:       
        print("button pressed")

    time.sleep_ms(500)
    ZOOM_RE = 1 * (zoom.read_u16() / 65535.0) #full signal=no zoom
    ZOOM_IM = 1.5 * (zoom.read_u16() / 65535.0) #full signal=no zoom
    OFFSET_RE = ((pan_x.read_u16() / 65535.0) - 0.5) * 5.5
    OFFSET_IM = ((pan_y.read_u16() / 65535.0) - 0.5) * 2.7
    print("zoom_re={}, zoom_im={}".format(ZOOM_RE,ZOOM_IM))
    print("offset_re ={}, offset_im={}".format(OFFSET_RE,OFFSET_IM))
        




