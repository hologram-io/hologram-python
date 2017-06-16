# PPP.py - Hologram Python SDK Modem PPP interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
import subprocess
import sys
from pppd import PPPConnection
from IPPP import IPPP
from Exceptions.HologramError import PPPError

DEFAULT_PPP_TIMEOUT = 200

class PPP(IPPP):

    def __init__(self, device_name='/dev/ttyUSB0', baud_rate='9600',
                 chatscript_file=None):


        super(PPP, self).__init__(device_name=device_name, baud_rate=baud_rate,
                                  chatscript_file=chatscript_file)

        try:
            self.__enforce_no_existing_ppp_session()
        except PPPError as e:
            self.logger.error(repr(e))
            sys.exit(1)

        self._ppp = PPPConnection(self.device_name, self.baud_rate, 'noipdefault',
                                  'usepeerdns', 'defaultroute', 'persist', 'noauth',
                                  connect=self.connect_script)

    def isConnected(self):
        return self._ppp.connected()

    # EFFECTS: Establishes a PPP connection. If this is successful, it will also
    #          reroute packets to ppp0 interface.
    def connect(self, timeout=DEFAULT_PPP_TIMEOUT):

        try:
            self.__enforce_no_existing_ppp_session()
        except PPPError as e:
            self.logger.error(repr(e))
            sys.exit(1)

        result = self._ppp.connect(timeout=timeout)

        if result == True:
            self.__reroute_packets()
        return result

    def disconnect(self):
        self.__shut_down_existing_ppp_session()
        return self._ppp.disconnect()

    # EFFECTS: Makes sure that there are no existing PPP instances on the same
    #          device interface.
    def __enforce_no_existing_ppp_session(self):


        process = self.__check_for_existing_ppp_sessions()

        if process is None:
            return

        pid = process.split(' ')[1]
        raise PPPError('An existing PPP session established by pid %s is currently using the %s device interface. Please close/kill that process first'
                         % (pid, self.device_name))

    def __shut_down_existing_ppp_session(self):
        process = self.__check_for_existing_ppp_sessions()

        if process is None:
            return

        pid = process.split(' ')[1]

        if pid is not None:
            kill_command = 'kill ' + str(pid)
            self.logger.info('Killing pid %s that currently have an active PPP session',
                         pid)
            subprocess.call(kill_command, shell=True)

    def __check_for_existing_ppp_sessions(self):
        self.logger.info('Checking for existing PPP sessions')
        out_list = subprocess.check_output(['ps', '--no-headers', '-axo',
                                            'pid,user,tty,args']).split('\n')

        # Get the end device name, ie. /dev/ttyUSB0 becomes ttyUSB0
        temp_device_name = self.device_name.split('/')[-1]

        # Iterate over all processes and find pppd with the specific device name we're using.
        for process in out_list:
            if 'pppd' in process and temp_device_name in process:
                self.logger.info('Found existing PPP session on %s', temp_device_name)
                return process

        return None

    def __reroute_packets(self):
        self.logger.info('Rerouting packets to ppp0 interface')
        subprocess.call('ip route add 10.176.0.0/16 dev ppp0', shell=True)
        subprocess.call('ip route add 10.254.0.0/16 dev ppp0', shell=True)
        subprocess.call('ip route add default dev ppp0', shell=True)

    @property
    def localIPAddress(self):
        return self._ppp.raddr

    @property
    def remoteIPAddress(self):
        return self._ppp.laddr
