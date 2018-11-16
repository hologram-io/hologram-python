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
import time
import threading
from subprocess import Popen, PIPE, STDOUT
from Exceptions.HologramError import PPPError, PPPConnectionError
import errno

__version__ = '1.0.3'
DEFAULT_CONNECT_TIMEOUT = 200

class PPPConnection(object):

    def __repr__(self):
        return type(self).__name__

    def __init__(self, *args, **kwargs):
        # Logging setup.
        self.logger = logging.getLogger(__name__)

        self._laddr = None
        self._raddr = None
        self.proc = None

        self.output = ''

        self._commands = []

        # This makes it harder to kill pppd so we're defaulting to it off for now
        # It's redudant anyway for the CLI
        if kwargs.pop('sudo', False):
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

        self.logger.info('Starting pppd')
        self.proc = Popen(self._commands, stdout=PIPE, stderr=STDOUT, universal_newlines=True)

        # set stdout to non-blocking
        fd = self.proc.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        result = False
        try:
            result = self.waitForPPPSuccess(timeout)
        except Exception as e:
            self.logger.error(e)

        if not result and self.proc and (self.proc.poll() is None):
            self.logger.debug('Killing pppd')
            self.proc.send_signal(signal.SIGTERM)
            time.sleep(1)

        return result


    def readFromPPP(self):
        try:
            self.output += self.proc.stdout.read()
        except IOError as e:
            if e.errno != errno.EAGAIN:
                raise
            time.sleep(1)


    def waitForPPPSuccess(self, timeout):
        starttime = time.time()
        while (time.time() - starttime) < timeout:
            self.readFromPPP()

            if self.laddr is not None and self.raddr is not None:
                return True

            if 'Modem hangup' in self.output:
                raise PPPError('Modem hangup - possibly due to an unregistered SIM')
            elif self.proc.poll():
                raise PPPConnectionError(self.proc.returncode, self.output)
        return False

    # EFFECTS: Disconnects from the network.
    def disconnect(self):
        if self.proc and self.proc.poll() is None:
            self.proc.send_signal(signal.SIGTERM)
            time.sleep(1)


    # EFFECTS: Returns true if a cellular connection is established.
    def connected(self):
        if self.proc and self.proc.poll():
            self.readFromPPP()
            if self.proc.returncode not in [0, 5]:
                raise PPPConnectionError(self.proc.returncode, self.output)
            return False
        elif self.laddr != None and self.raddr != None:
            return True

        return False

    # EFFECTS: Returns the local IP address.
    @property
    def laddr(self):
        if self.proc and not self._laddr:
            self.readFromPPP()
            result = re.search(r'local  IP address ([\d\.]+)', self.output)
            if result:
                self._laddr = result.group(1)

        return self._laddr

    # EFFECTS: Returns the remote IP address.
    @property
    def raddr(self):
        if self.proc and not self._raddr:
            self.readFromPPP()
            result = re.search(r'remote IP address ([\d\.]+)', self.output)
            if result:
                self._raddr = result.group(1)

        return self._raddr

