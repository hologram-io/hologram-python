# -*- coding: utf-8 -*-
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

class SMS(object):

    def __init__(self, sender, timestamp, message):
        self.sender = sender
        self.timestamp = timestamp
        self.message = message

    def __repr__(self):

        temp_str = type(self).__name__ + ': '
        temp_str = temp_str + 'sender: ' + self.sender + ', '
        temp_str = temp_str + 'timestamp: ' + self.timestamp.strftime('%c') + ', '
        temp_str = temp_str + 'message: ' + self.message

        return temp_str

class ModemResult:
    Invalid = 'Invalid'
    NoMatch = 'NoMatch'
    Error = 'Error'
    Timeout = 'Timeout'
    OK = 'OK'

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
