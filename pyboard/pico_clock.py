# *****************************************************************************
# * | File        :   Pico_ePaper-2.9.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2021-03-16
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from machine import Pin, SPI
from pico_datetime import localTime, setRTC
#import framebuf
import adafruit_framebuf as framebuf
import utime
import ustruct

days = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
months = ('OBOB', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
# Display resolution
EPD_WIDTH  = const(128)
EPD_HEIGHT = const(296)

# Display commands
DRIVER_OUTPUT_CONTROL                = const(0x01)
BOOSTER_SOFT_START_CONTROL           = const(0x0C)
#GATE_SCAN_START_POSITION             = const(0x0F)
DEEP_SLEEP_MODE                      = const(0x10)
DATA_ENTRY_MODE_SETTING              = const(0x11)
SW_RESET                             = const(0x12)
#TEMPERATURE_SENSOR_CONTROL           = const(0x1A)
MASTER_ACTIVATION                    = const(0x20)
DISPLAY_UPDATE_CONTROL_1             = const(0x21)
DISPLAY_UPDATE_CONTROL_2             = const(0x22)
WRITE_RAM                            = const(0x24)
WRITE_RAM_2                           = const(0x26)
WRITE_VCOM_REGISTER                  = const(0x2C)
WRITE_LUT_REGISTER                   = const(0x32)
SET_DUMMY_LINE_PERIOD                = const(0x3A)
SET_GATE_TIME                        = const(0x3B)
BORDER_WAVEFORM_CONTROL              = const(0x3C)
SET_RAM_X_ADDRESS_START_END_POSITION = const(0x44)
SET_RAM_Y_ADDRESS_START_END_POSITION = const(0x45)
SET_RAM_X_ADDRESS_COUNTER            = const(0x4E)
SET_RAM_Y_ADDRESS_COUNTER            = const(0x4F)
TERMINATE_FRAME_READ_WRITE           = const(0xFF)

ROTATE_0   = const(0)
ROTATE_90  = const(1)
ROTATE_180 = const(2)
ROTATE_270 = const(3)
ROTATE_360 = const(4) # use with range(ROTATE_360)

BLACK = const(0)
WHITE = const(1)
BUSY = const(1)  # 1=busy, 0=idle
RST_PIN         = const(12)
DC_PIN          = const(8)
CS_PIN          = const(9)
BUSY_PIN        = const(13)

WF_PARTIAL_2IN9 = [
    0x0,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x80,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x40,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0A,0x0,0x0,0x0,0x0,0x0,0x2,  
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x22,0x22,0x22,0x22,0x22,0x22,0x0,0x0,0x0,
    0x22,0x17,0x41,0xB0,0x32,0x36,
]

class EPD_2in9(framebuf.FrameBuffer):
    def __init__(self, buffer):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.rotate = ROTATE_90
        self.lut = WF_PARTIAL_2IN9
        self.busy_pin.init(self.busy_pin.IN)
        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)

        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.width, self.height, framebuf.MHMSB)
        
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50) 
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)   

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
        
    def ReadBusy(self):
        print("e-Paper busy")
        while(self.digital_read(self.busy_pin) == 1):      #  0: idle, 1: busy
            self.delay_ms(10) 
        print("e-Paper busy release")  

    def TurnOnDisplay(self):
        self.send_command(DISPLAY_UPDATE_CONTROL_2) # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0xF7)
        self.send_command(MASTER_ACTIVATION) # MASTER_ACTIVATION
        self.ReadBusy()

    def TurnOnDisplay_Partial(self):
        self.send_command(DISPLAY_UPDATE_CONTROL_2) # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0x0F)
        self.send_command(MASTER_ACTIVATION) # MASTER_ACTIVATION
        self.ReadBusy()

    def SendLut(self):
        self.send_command(WRITE_LUT_REGISTER)
        for i in range(0, 153):
            self.send_data(self.lut[i])
        self.ReadBusy()

    def SetWindow(self, x_start, y_start, x_end, y_end):
        self.send_command(SET_RAM_X_ADDRESS_START_END_POSITION) # SET_RAM_X_ADDRESS_START_END_POSITION
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x_start>>3) & 0xFF)
        self.send_data((x_end>>3) & 0xFF)
        self.send_command(SET_RAM_Y_ADDRESS_START_END_POSITION) # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    def SetCursor(self, x, y):
        self.send_command(SET_RAM_X_ADDRESS_COUNTER) # SET_RAM_X_ADDRESS_COUNTER
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data(x & 0xFF)
        
        self.send_command(SET_RAM_Y_ADDRESS_COUNTER) # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
        self.ReadBusy()
        
    def init(self):
        # EPD hardware init start     
        self.reset()

        self.ReadBusy();   
        self.send_command(SW_RESET);  #SW_RESET
        self.ReadBusy();   

        self.send_command(DRIVER_OUTPUT_CONTROL); #Driver output control      
        self.send_data(0x27);
        self.send_data(0x01);
        self.send_data(0x00);
    
        self.send_command(DATA_ENTRY_MODE_SETTING); #data entry mode       
        self.send_data(0x03);

        self.SetWindow(0, 0, self.width-1, self.height-1);

        self.send_command(DISPLAY_UPDATE_CONTROL_1); #  Display update control
        self.send_data(0x00);
        self.send_data(0x80);   
    
        self.SetCursor(0, 0);
        self.ReadBusy();
        # EPD hardware init end
        return 0
    
    def set_frame_memory(self, image, x, y, w, h):
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.display(image)

    def display(self, image):
        if (image == None):
            return            
        self.send_command(WRITE_RAM) # 0x24) # WRITE_RAM
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(image[i + j * int(self.width / 8)])   
        self.TurnOnDisplay()

    def display_Base(self, image):
        if (image == None):
            return   
        self.send_command(WRITE_RAM) # WRITE_RAM
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(image[i + j * int(self.width / 8)])
                
        self.send_command(WRITE_RAM_2) #0x26) # WRITE_RAM?2
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(image[i + j * int(self.width / 8)])   
                
        self.TurnOnDisplay()
        
    def display_Partial(self, image):
        if (image == None):
            return
            
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(2)   
        
        self.SendLut();
        self.send_command(0x37); 
        self.send_data(0x00);  
        self.send_data(0x00);  
        self.send_data(0x00);  
        self.send_data(0x00); 
        self.send_data(0x00);   
        self.send_data(0x40);  
        self.send_data(0x00);  
        self.send_data(0x00);   
        self.send_data(0x00);  
        self.send_data(0x00);

        self.send_command(BORDER_WAVEFORM_CONTROL) #0x3C); #BorderWavefrom
        self.send_data(0x80);

        self.send_command(DISPLAY_UPDATE_CONTROL_2); 
        self.send_data(0xC0);   
        self.send_command(0x20); 
        self.ReadBusy();

        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)
        
        self.send_command(WRITE_RAM) # WRITE_RAM
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(image[i + j * int(self.width / 8)])
        self.TurnOnDisplay_Partial()

    def Clear(self, color):
        self.send_command(WRITE_RAM) # WRITE_RAM
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(color)
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(DEEP_SLEEP_MODE) # DEEP_SLEEP_MODE
        self.send_data(0x01)
        
        self.delay_ms(2000)
        self.module_exit()
        
    def wait_until_idle(self):
        while self.busy_pin.value() == BUSY:
            sleep_ms(100)

def initFrameBuffer(buffer):
    fb = framebuf.FrameBuffer(buffer, EPD_WIDTH, EPD_HEIGHT, framebuf.MHMSB)
    return fb
    
def initEPD(fb):
    epd = EPD_2in9(fb)
    return epd
    
def height_test():
    astring='1234567890'
    fb.fill(WHITE)
    fb.rotation = ROTATE_90 # 90 DEGREES
    for height in range(6, 10):
        print("Height:{}".format(height))
        fb.text(str(height), 0, 0, BLACK, size=height)
        fb.text(astring, 0, round(EPD_WIDTH/2), BLACK, size=height)
        epd.display(buffer)
        fb.fill(WHITE)
    for height in range(10, 14):
        print("Height:{}".format(height))
        fb.text(str(height), 0, 0, BLACK, size=height)
        fb.text(str(height), round(EPD_HEIGHT/2), 0, BLACK, size=height)
        epd.display(buffer)
        fb.fill(WHITE)
    for height in range(14, 20):
        print("Height:{}".format(height))
        fb.text(str(height), 0, 0, BLACK, size=height)
        epd.display(buffer)
        fb.fill(WHITE)

def width_test():
    astring='1234567890'
    fb.fill(WHITE)
    fb.rotation = ROTATE_90 # 90 DEGREES

    fb.text(astring*8, 0, 0, BLACK, size=1) #39
    fb.text(astring*6, 0, 10, BLACK, size=2) #24
    fb.text(astring*4, 0, 30, BLACK, size=3)  #16  
    fb.text(astring*2, 0, 56, BLACK, size=4) #12
    fb.text(astring, 0, 95, BLACK, size=5) #10
    epd.display(buffer)
    
def init_paper():
    buffer = bytearray(round(EPD_WIDTH * EPD_HEIGHT / 8))
    fb = initFrameBuffer(buffer)
    epd = initEPD(buffer)
    return buffer, fb, epd
    
def suffix_day(d):
    ''' Add the correct suffix for a day between the 1st and 31st '''
    if d == 1 or d == 21 or d == 31:
        d = "".join((str(d), 'st, '))
    elif d == 2 or d == 22:
        d = "".join((str(d), 'nd, '))
    elif d == 3 or d == 23:
        d = "".join((str(d), 'rd, '))
    else:
        d = "".join((str(d), 'th, '))
    return d

def center_x(word, size):
    ''' x coord for centering string at different sizes and rotated 90 degrees '''
    ppc = {1:6, 2:12, 3:18, 4:24, 5:30} # pixels per character
    x = round((EPD_HEIGHT - len(word) * ppc[size])/2)
    print("x coord: ", x)
    return x
    
def updateClock(year, month, date, hour, minute, seconds, weekday, yearday):
    TOP_MARGIN = 32
    LEFT_MARGIN = 10
    RADIUS = 5
    fb.fill(WHITE)
    fb.rotation = ROTATE_90 # 90 DEGREES
    line1 = days[weekday]
    fb.text(line1, center_x(line1, size=4), 0, BLACK, size=4)
    #fb.vline(round(EPD_HEIGHT/2-LEFT_MARGIN/2), TOP_MARGIN, EPD_WIDTH-TOP_MARGIN, BLACK)
#     fb.vline(120, 90, 60, 0x00)

   # fb.hline(LEFT_MARGIN, round(EPD_WIDTH/2+TOP_MARGIN/2), EPD_HEIGHT-LEFT_MARGIN, BLACK)
   # fb.circle(round(EPD_HEIGHT/2-LEFT_MARGIN/2), round(EPD_WIDTH/2+TOP_MARGIN/2), RADIUS, BLACK)
    
    line2 = months[month] + ' ' + suffix_day(date) + str(year)
    fb.text(line2, center_x(line2, 3), round(EPD_WIDTH/3), BLACK, size=3) #month
    #fb.text(str(hour), LEFT_MARGIN*5, round(EPD_WIDTH * 3/4), BLACK, size=3) #day
    
    #fb.text(str(date), round(EPD_HEIGHT/2) + LEFT_MARGIN*2, round(EPD_WIDTH/3), BLACK, size=3) #hour
    
    if minute < 10:
        pad_minute = ':0'+str(minute)
    else:
        pad_minute = ':'+str(minute)
    if hour < 13:
        line3 = str(hour)+pad_minute+' AM'
    else:
        line3 = str(hour-12)+pad_minute+' PM'
    fb.text(line3, center_x(line3,5), round(EPD_WIDTH * 3/4-15), BLACK, size=5) #day
    #fb.text(, round(EPD_HEIGHT/2) + LEFT_MARGIN*2, round(EPD_WIDTH * 3/4), BLACK, size=3) #minute
    
    for ring in range(3,2,12):
        fb.circle(round(EPD_HEIGHT/2-LEFT_MARGIN/2), round(EPD_WIDTH/2+TOP_MARGIN/2-10), RADIUS*ring, BLACK)

def prompt_time():

    fb.fill(WHITE)
    fb.rotation = ROTATE_90 # 90 DEGREES
    astring = 'Enter Time'
    fb.text(astring*8, 0, round(EPD_WIDTH/3), BLACK, size=5) #39
    epd.display(buffer)
    setRTC()
    
def run_clock():
    prompt_time()
    while True:
        time = utime.localtime()
        print(time)
        updateClock(*time) # the update takes about 5 seconds
        epd.display(buffer)
        utime.sleep(55) 
        
if __name__=='__main__':
    buffer, fb, epd = init_paper()
#     epd.Clear(WHITE)
#     height_test(fb)
#     utime.sleep(2)
#     width_test(fb)
#     utime.sleep(5)


    run_clock()
    
    
