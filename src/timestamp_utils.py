import datetime

def changeMonthValue(month):
    if month == 'Jan':
        return '01'
    if month == 'Feb':
        return '02'
    if month == 'Mar':
        return '03'
    if month == 'Apr':
        return '04'
    if month == 'May':
        return '05'
    if month == 'Jun':
        return '06'
    if month == 'Jul':
        return '07'
    if month == 'Aug':
        return '08'
    if month == 'Sep':
        return '09'
    if month == 'Oct':
        return '10'
    if month == 'Nov':
        return '11'
    if month == 'Dec':
        return '12'
    return ''

def getTimestampFromPubdate(pubdate):
    date_strs = pubdate.split(' ')
    timestamp = date_strs[3] + changeMonthValue(date_strs[2]) + date_strs[1] + date_strs[4]
    timestamp = timestamp.replace(':', '')
    return timestamp

def getTimeZoneValue(timezoneStr):
    if timezoneStr == 'GMT':
        return 0
    if timezoneStr[0] == '+' or timezoneStr[0] == '-':
        return int(timezoneStr[:3])
    return 0

def adjustTimeByTimezon(year, month, date, hh, MM, ss, zone):
    zone = 0 - zone
    t = datetime.datetime(year, month, date, hh, MM, ss) + datetime.timedelta(hours=zone)
    return (t.year, t.month, t.day, t.hour, t.minute, t.second)

def getTimeDecFromPubdate(pubdate):
    date_strs = pubdate.split(' ')
    year = int(date_strs[3])
    month = int(changeMonthValue(date_strs[2]))
    date = int(date_strs[1])
    time_strs = date_strs[4].split(':')
    hh = int(time_strs[0])
    MM = int(time_strs[1])
    ss = int(time_strs[2])
    time_zone_value = getTimeZoneValue(date_strs[5])
    return adjustTimeByTimezon(year, month, date, hh, MM, ss, time_zone_value)

if __name__ == '__main__':
    pubdate = 'Fri, 30 Nov 2018 11:08:19 +0800'
    print(pubdate)
    print(getTimestampFromPubdate(pubdate))
    print(getTimeDecFromPubdate(pubdate))
