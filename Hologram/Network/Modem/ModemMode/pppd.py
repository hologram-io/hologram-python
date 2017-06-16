# pppd.py - Modified to satisfy Hologram's PPP requirements.
#
# Copyright (c) 2016 Michael de Villiers
#
# Original Author: Michael de Villiers
# Original source code: https://github.com/cour4g3/python-pppd
#
# LICENSE: Distributed under the terms of the MIT License

import fcntl
import logging
from logging import NullHandler
import os
import re
import signal
import sys
import time
import threading
from subprocess import Popen, PIPE, STDOUT
from Exceptions.HologramError import PPPError, PPPConnectionError

__version__ = '1.0.3'
DEFAULT_CONNECT_TIMEOUT = 200

class PPPConnection(object):

    def __repr__(self):
        return type(self).__name__

    def __init__(self, *args, **kwargs):
        # Logging setup.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(NullHandler())

        self._laddr = None
        self._raddr = None
        self._connectThread = None
        self._outputRWLock = threading.Condition()
        self._outputReadyToRead = True
        self.proc = None

        self.output = ''

        self._commands = []

        if kwargs.pop('sudo', True):
            sudo_path = kwargs.pop('sudo_path', '/usr/bin/sudo')
            if not os.path.isfile(sudo_path) or not os.access(sudo_path, os.X_OK):
                raise IOError('%s not found' % sudo_path)
            self._commands.append(sudo_path)

        pppd_path = kwargs.pop('pppd_path', '/usr/sbin/pppd')
        if not os.path.isfile(pppd_path) or not os.access(pppd_path, os.X_OK):
            raise IOError('%s not found' % pppd_path)

        self._commands.append(pppd_path)

        for k,v in kwargs.items():
            self._commands.append(k)
            self._commands.append(v)
        self._commands.extend(args)
        self._commands.append('nodetach')


    # EFFECTS: Spins out a new thread that connects to the network with a given
    #          timeout value. Default to DEFAULT_CONNECT_TIMEOUT seconds.
    #          Returns true if successful, false otherwise.
    def connect(self, timeout = DEFAULT_CONNECT_TIMEOUT):

        self.proc = Popen(self._commands, stdout=PIPE, stderr=STDOUT, universal_newlines=True)

        # set stdout to non-blocking
        fd = self.proc.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        result = [False]

        self._connectThread = threading.Thread(target = self.connectThreadedFunc,
                                               args = [result])
        self._connectThread.daemon = True
        self._connectThread.start()
        self._connectThread.join(timeout)

        # If thread is still alive, tear down pppd connection and kill the thread.
        if self._connectThread.is_alive():
            self._connectThread.join(1)
            self.proc.send_signal(signal.SIGTERM)
            time.sleep(1)

        return result[0]

    # EFFECTS: Establish a cellular connection. Returns true if successful,
    #          false otherwise.
    def connectThreadedFunc(self, result):

        while True:
            try:
                self.output += self.proc.stdout.read()
            except IOError as e:
                if e.errno != 11:
                    raise
                time.sleep(1)

            if self.laddr != None and self.raddr != None:
                result[0] = True
                return

            try:
                if 'Modem hangup' in self.output:
                    raise PPPError('Modem hangup - possibly due to an unregistered SIM')
                elif self.proc.poll():
                    raise PPPConnectionError(self.proc.returncode, self.output)
            except (PPPError, PPPConnectionError) as e:
                self.logger.error(repr(e))
                sys.exit(1)

    # EFFECTS: Disconnects from the network.
    #          Returns true if successful, false otherwise.
    def disconnect(self):

        try:
            if not self.connected():
                return False
        except PPPConnectionError:
            return False

        self.proc.send_signal(signal.SIGTERM)
        time.sleep(1)

        return True

    # EFFECTS: Returns true if a cellular connection is established.
    def connected(self):
        if self.proc and self.proc.poll():
            try:
                self.output += self.proc.stdout.read()
            except IOError as e:
                if e.errno != 11:
                    raise
            if self.proc.returncode not in [0, 5]:
                raise PPPConnectionError(proc.returncode, self.output)
            return False
        elif self.laddr != None and self.raddr != None:
            return True

        return False

    # EFFECTS: Returns the local IP address.
    @property
    def laddr(self):
        if self.proc and not self._laddr:
            try:
                self.output += self.proc.stdout.read()
            except IOError as e:
                if e.errno != 11:
                    raise
            result = re.search(r'local  IP address ([\d\.]+)', self.output)
            if result:
                self._laddr = result.group(1)

        return self._laddr

    # EFFECTS: Returns the remote IP address.
    @property
    def raddr(self):
        if self.proc and not self._raddr:
            try:
                self.output += self.proc.stdout.read()
            except IOError as e:
                if e.errno != 11:
                    raise
            result = re.search(r'remote IP address ([\d\.]+)', self.output)
            if result:
                self._raddr = result.group(1)

        return self._raddr

    @property
    def output(self):
        self._outputRWLock.acquire()

        while not self._outputReadyToRead:
            self._outputRWLock.wait()

        self._outputReadyToRead = True
        self._outputRWLock.release()
        return self._output

    @output.setter
    def output(self, output):
        self._outputReadyToRead = False
        self._outputRWLock.acquire()
        self._output = output
        self._outputReadyToRead = True
        self._outputRWLock.notifyAll()
        self._outputRWLock.release()
