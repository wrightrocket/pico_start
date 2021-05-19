# *****************************************************************************
# * | File        :	  Pico_ePaper-2.9.py
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
#import framebuf
import adafruit_framebuf as framebuf
import utime
from image_dark import hello_world_dark
from image_light import hello_world_light
import ustruct

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

BLACK = 0
WHITE = 1
BUSY = const(1)  # 1=busy, 0=idle
RST_PIN         = 12
DC_PIN          = 8
CS_PIN          = 9
BUSY_PIN        = 13

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
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.rotate = ROTATE_0
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
    
    def set_rotate(self, rotate):
        if (rotate == ROTATE_0):
            self.rotate = ROTATE_0
            self.width = epdif.EPD_WIDTH
            self.height = epdif.EPD_HEIGHT
        elif (rotate == ROTATE_90):
            self.rotate = ROTATE_90
            self.width = epdif.EPD_HEIGHT
            self.height = epdif.EPD_WIDTH
        elif (rotate == ROTATE_180):
            self.rotate = ROTATE_180
            self.width = epdif.EPD_WIDTH
            self.height = epdif.EPD_HEIGHT
        elif (rotate == ROTATE_270):
            self.rotate = ROTATE_270
            self.width = epdif.EPD_HEIGHT
            self.height = epdif.EPD_WIDTH

    def set_pixel(self, frame_buffer, x, y, colored):
        if (x < 0 or x >= self.width or y < 0 or y >= self.height):
            return
        if (self.rotate == ROTATE_0):
            self.set_absolute_pixel(frame_buffer, x, y, colored)
        elif (self.rotate == ROTATE_90):
            point_temp = x
            x = epdif.EPD_WIDTH - y
            y = point_temp
            self.set_absolute_pixel(frame_buffer, x, y, colored)
        elif (self.rotate == ROTATE_180):
            x = epdif.EPD_WIDTH - x
            y = epdif.EPD_HEIGHT- y
            self.set_absolute_pixel(frame_buffer, x, y, colored)
        elif (self.rotate == ROTATE_270):
            point_temp = x
            x = y
            y = epdif.EPD_HEIGHT - point_temp
            self.set_absolute_pixel(frame_buffer, x, y, colored)

    def set_absolute_pixel(self, frame_buffer, x, y, colored):
        # To avoid display orientation effects
        # use EPD_WIDTH instead of self.width
        # use EPD_HEIGHT instead of self.height
        if (x < 0 or x >= EPD_WIDTH or y < 0 or y >= EPD_HEIGHT):
            return
        if (colored):
            frame_buffer[(x + y * EPD_WIDTH) // 8] &= ~(0x80 >> (x % 8))
        else:
            frame_buffer[(x + y * EPD_WIDTH) // 8] |= 0x80 >> (x % 8)

    def set_frame_memory(self, image, x, y, w, h):
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.display(image)
#         x = x & 0xF8
#         w = w & 0xF8
# 
#         if (x + w >= self.width):
#             x_end = self.width - 1
#         else:
#             x_end = x + w - 1
# 
#         if (y + h >= self.height):
#             y_end = self.height - 1
#         else:
#             y_end = y + h - 1
# 
#         self.set_memory_area(x, y, x_end, y_end)
#         self.set_memory_pointer(x, y)
#         self.send_command(WRITE_RAM)
#         self.send_data(image)
        
      # specify the memory area for data R/W
    def set_memory_area(self, x_start, y_start, x_end, y_end):
        self.send_command(SET_RAM_X_ADDRESS_START_END_POSITION)
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x_start >> 3) & 0xff)
        self.send_data((x_end >> 3) & 0xFF)
        self.send_command(SET_RAM_Y_ADDRESS_START_END_POSITION)
        self.send_data((y_start >> 3) & 0xff)
        self.send_data((y_end >> 3) & 0xFF)

    def set_memory_pointer(self, x, y):
        self.send_command(SET_RAM_X_ADDRESS_COUNTER)
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x >> 3) & 0xFF)
        self.send_command(SET_RAM_Y_ADDRESS_COUNTER)
        self.send_data((y >> 3) & 0xFF)
        self.wait_until_idle()
        
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

    
if __name__=='__main__':
    
    epd = EPD_2in9()
    #epd.Clear(0xff)
    epd.init()
#     
#     epd.fill(0xff)
#     epd.text("Wright Rocket", 5, 10, 0x00)
#     epd.text("Pico_ePaper-2.9", 5, 40, 0x00)
#     epd.text("Raspberry Pico", 5, 70, 0x00)
#     epd.display(epd.buffer)
#     epd.delay_ms(2000)
#     epd.set_rotate(90)
    
    # epd.set_pixel(epd.buffer, 0, 0, 0xff)
    buffer = bytearray(round(EPD_WIDTH * EPD_HEIGHT / 8))
    fb = framebuf.FrameBuffer(buffer, EPD_WIDTH, EPD_HEIGHT, framebuf.MHMSB)
    fb.fill(WHITE)
    
#     
#     epd.set_frame_memory(hello_world_dark, 0, 0, EPD_WIDTH, EPD_HEIGHT)
#     print('hw_dark')
#     epd.delay_ms(2000)
#     epd.set_frame_memory(hello_world_light, 0, 0, EPD_WIDTH, EPD_HEIGHT)
#     print('hw_light')
    #epd.display(epd.buffer)
    fb.rotation = 1 # 90 DEGREES
    TOP_MARGIN = 32
    LEFT_MARGIN = 10
    RADIUS = 5
    fb.text('WrightRocket', 75, 8, BLACK, size=2)
    fb.vline(round(EPD_HEIGHT/2-LEFT_MARGIN/2), TOP_MARGIN, EPD_WIDTH-TOP_MARGIN, BLACK)
#     fb.vline(120, 90, 60, 0x00)
    fb.hline(LEFT_MARGIN, round(EPD_WIDTH/2+TOP_MARGIN/2), EPD_HEIGHT-LEFT_MARGIN, BLACK)
    fb.circle(round(EPD_HEIGHT/2-LEFT_MARGIN/2), round(EPD_WIDTH/2+TOP_MARGIN/2), RADIUS, BLACK)
#     epd.hline(10, 150, 110, 0x00)
#     epd.line(10, 90, 120, 150, 0x00)
#     epd.line(120, 90, 10, 150, 0x00)
    epd.display(buffer)
    epd.delay_ms(2000)
    for ring in range(2,10):
        fb.circle(round(EPD_HEIGHT/2-LEFT_MARGIN/2), round(EPD_WIDTH/2+TOP_MARGIN/2), RADIUS*ring, BLACK)
    
    epd.display(buffer)
    print(buffer)
#     
#     epd.rect(10, 180, 50, 80, 0x00)
#     epd.fill_rect(70, 180, 50, 80, 0x00)
#     epd.display_Base(epd.buffer)
#     epd.delay_ms(2000)
#     
#     for i in range(0, 10):
#         epd.fill_rect(40, 270, 40, 10, 0xff)
#         epd.text(str(i), 60, 270, 0x00)
#         epd.display_Partial(epd.buffer)
        
#     epd.init()
#     epd.Clear(0xff)
#     epd.delay_ms(2000)
    print("sleep")
#     epd.sleep()