#!/usr/bin/env python3
#
# Vendor:Product ID for Raspberry Pi Pico is 2E8A:0005
#
# see section 4.8 RTC of https://datasheets.raspberrypi.org/rp2040/rp2040-datasheet.pdf and in particular section 4.8.6 
# for the RTC_BASE address (0x4005C000) and details of the RD2040 setup registers used to program the RTC
#
from serial.tools import list_ports
import serial, time

picoPorts = list(list_ports.grep("2E8A:0005"))

utcTime = str( int(time.time()) )
pythonInject = [
    'import machine\r\n',
    'import utime\r\n',
    'rtc_base_mem = 0x4005c000\r\n',
    'atomic_bitmask_set = 0x2000\r\n',
    'led_onboard = machine.Pin(25, machine.Pin.OUT)\r\n',
    '(year,month,day,hour,minute,second,wday,yday)=utime.localtime('+utcTime+')'+'\r\n',
    'machine.mem32[rtc_base_mem + 4] = (year << 12) | (month  << 8) | day\r\n',
    'machine.mem32[rtc_base_mem + 8] = ((hour << 16) | (minute << 8) | second) | (((wday + 1) % 7) << 24)\r\n',
    'machine.mem32[rtc_base_mem + atomic_bitmask_set + 0xc] = 0x10\r\n',
    'for i in range(5):\r\n',
    '    led_onboard.toggle()\r\n',
    '    utime.sleep(0.03)\r\n',
    'led_onboard.value(0)\r\n'
    ]

if not picoPorts:
    print("No Raspberry Pi Pico found")
else:
    picoSerialPort = picoPorts[0].device
    with serial.Serial(picoSerialPort) as s:
        s.write(b'\x03')
        s.write(b'\x03')
        s.write(b'\x01')       
        for n in range(len(pythonInject)):
            s.write(bytes(pythonInject[n], 'ascii'))
        time.sleep(0.1) 
        s.write(b'\x04')
        s.write(b'\x02')
    print( 'Raspberry Pi Pico found at '+str(picoSerialPort)+'\r' )
    print( 'Host computer epoch synchronised over USB serial: '+utcTime+'\r' )