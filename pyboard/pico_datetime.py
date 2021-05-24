import machine
import utime
ctime = None

def timeInput():
    print()
    print("                           YYYY MM DD HH MM SS")
    entry = input ("Enter current date & time: ")
    return entry

def convertTime(dateTime):
    if not dateTime:
        return utime.localtime()
    else:
        dateTime += ' 0 0'
        givenTime = utime.mktime(list(map(int, tuple(dateTime.split(' ')))))
        ctime=utime.localtime(givenTime)
    return ctime
    
def setRTC():
    
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
    
    # prepare to insert data into the rtc
    ctime = convertTime(timeInput())

    setup_0 = (ctime[0] << 12) | (ctime[1] << 8) | ctime[2]

    setup_1 =  (ctime[3] << 16) | (ctime[4] << 8) | ctime[5]
    setup_1 =  setup_1 |  (weekDay(ctime[0],ctime[1],ctime[2]) << 24)
    # Be aware that RTC start at sunday=0
    # and utime start dayofweek monday=0

    # set rtc
    machine.mem32[0x4005c004]= setup_0
    machine.mem32[0x4005c008]= setup_1
    machine.mem8[0x4005c00c] = machine.mem8[0x4005c00c] | 0x10

def localTime():
    '''
    Use to retreive the localtime
    
    0   tm_year (for example, 1993)
    1   tm_mon  range [1, 12]
    2   tm_mday range [1, 31]
    3   tm_hour range [0, 23]
    4   tm_min  range [0, 59]
    5   tm_sec  range [0, 61]
    6   tm_wday range [0, 6], Monday is 0
    7   tm_yday range [1, 366]
    '''
    return utime.localtime()

def dateTime():
    '''
    return the month, day, hour and minute
    '''
    
    return localTime()[1:6]

if __name__ == '__main__':
    print('Use setRTC() to set the time and localTime() to retrieve it')