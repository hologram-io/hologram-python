# UtilClasses.py - Hologram Python SDK Util classes
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

import threading

class Location(object):

    def __init__(self, date=None, time=None, latitude=None, longitude=None,
                altitude=None, uncertainty=None):
        self.date = date
        self.time = time
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.uncertainty = uncertainty

    def __repr__(self):
        return type(self).__name__

class Timestamp(object):

    def __init__(self, year=None, month=None, day=None, hour=None, minute=None,
                 second=None, tzquarter=None):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.tzquarter = tzquarter

    def __repr__(self):
        temp_str = type(self).__name__ + ': '
        temp_str = temp_str + 'year: ' + repr(self.year) + ', '
        temp_str = temp_str + 'month: ' + repr(self.month) + ', '
        temp_str = temp_str + 'day: ' + repr(self.day) + ', '
        temp_str = temp_str + 'hour: ' + repr(self.hour) + ', '
        temp_str = temp_str + 'minute: ' + repr(self.minute) + ', '
        temp_str = temp_str + 'second: ' + repr(self.second) + ', '
        temp_str = temp_str + 'tzquarter: ' + repr(self.tzquarter)

        return temp_str

class SMS(object):

    def __init__(self, sender='', timestamp=Timestamp(), message=''):
        self.sender = sender
        self.timestamp = timestamp
        self.message = message

    def __repr__(self):

        temp_str = type(self).__name__ + ': '
        temp_str = temp_str + 'sender: ' + self.sender + ', '
        temp_str = temp_str + 'timestamp: ' + repr(self.timestamp) + ', '
        temp_str = temp_str + 'message: ' + self.message

        return temp_str

class RWLock(object):

    def __init__(self):
        self.mutex = threading.Condition()
        self.readers = 0
        self.writer = False

    def acquire(self):
        self.writer_acquire()

    def release(self):
        self.writer_release()

    def reader_acquire(self):
        self.mutex.acquire()
        while self.writer:
            self.mutex.wait()
        self.readers += 1
        self.mutex.release()

    def reader_release(self):
        self.mutex.acquire()
        self.readers -= 1
        if self.readers == 0:
            self.mutex.notifyAll()
        self.mutex.release()

    def writer_acquire(self):
        self.mutex.acquire()
        while self.writer or self.readers > 0:
            self.mutex.wait()
        self.writer = True
        self.mutex.release()

    def writer_release(self):
        self.mutex.acquire()
        self.writer = False
        self.mutex.notifyAll()
        self.mutex.release()
