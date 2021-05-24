import machine
import utime
print()
print("                           YYYY MM DD HH MM SS")
dateTime = (input ("Enter current date & time: "))+' 0 0'
givenTime = utime.mktime(list(map(int, tuple(dateTime.split(' ')))))

ctime=utime.localtime(givenTime)

# ok insert data into the rtc

setup_0 = (ctime[0] << 12) | (ctime[1] << 8) | ctime[2]

def weekDay(year, month, day):
    offset = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    afterFeb = 1
    if month > 2: afterFeb = 0
    aux = year - 1700 - afterFeb
    # dayOfWeek for 1700/1/1 = 5, Friday
    dayOfWeek  = 5
    # partial sum of days betweem current date and 1700/1/1
    dayOfWeek += (aux + afterFeb) * 365                  
    # leap year correction    
    dayOfWeek += aux // 4 - aux // 100 + (aux + 100) // 400     
    # sum monthly and day offsets
    dayOfWeek += offset[month - 1] + (day - 1)               
    dayOfWeek %= 7
    return int(dayOfWeek)

setup_1 =  (ctime[3] << 16) | (ctime[4] << 8) | ctime[5]
setup_1 =  setup_1 |  (weekDay(ctime[0],ctime[1],ctime[2]) << 24)
# Be aware that RTC start at sunday=0
# and utime start dayofweek monday=0

# set rtc
machine.mem32[0x4005c004]= setup_0
machine.mem32[0x4005c008]= setup_1
machine.mem8[0x4005c00c] = machine.mem8[0x4005c00c] | 0x10

def localtime():
    return utime.localtime()
