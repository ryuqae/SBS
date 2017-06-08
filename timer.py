# coding: utf-8

from datetime import datetime, timedelta

def date_to_date(date):
    year, month, day = map(int, [date[0:4], date[4:6], date[6:8]])
    return datetime(year, month, day)

def time_to_delta(time):
    hours, minutes, seconds = map(int, [time[0:2], time[2:4], time[4:6]])
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


if __name__ == '__main__':
    print('===== Test Code =====')
    d = input('Type original date in string(YYYYMMDD) : ')
    t = input('Type original time in string(HHMMSS) : ')
    print('Typed string \'%s\' and \'%s\' is converted to %s' % (d, t, date_to_date(d) + time_to_delta(t)))
    print('===== Test End =====')



