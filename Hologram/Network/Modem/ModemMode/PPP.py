# PPP.py - Hologram Python SDK Modem PPP interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#
import psutil
from pppd import PPPConnection
from IPPP import IPPP
from Hologram.Network.Route import Route
from Exceptions.HologramError import PPPError

DEFAULT_PPP_TIMEOUT = 200
DEFAULT_PPP_INTERFACE = 'ppp0'
MAX_PPP_INTERFACE_UP_RETRIES = 10
MAX_REROUTE_PACKET_RETRIES = 15


class PPP(IPPP):

    def __init__(self, device_name='/dev/ttyUSB0', all_attached_device_names=[],
                 baud_rate='9600', chatscript_file=None):

        super(PPP, self).__init__(device_name=device_name, baud_rate=baud_rate,
                                  chatscript_file=chatscript_file)

        self.route = Route()
        self.all_attached_device_names = all_attached_device_names
        self._ppp = PPPConnection(self.device_name, self.baud_rate, 'noipdefault',
                                  'usepeerdns', 'persist', 'noauth',
                                  connect=self.connect_script)

    def isConnected(self):
        return self._ppp.connected()

    # EFFECTS: Establishes a PPP connection. If this is successful, it will also
    #          reroute packets to ppp0 interface.
    def connect(self, timeout=DEFAULT_PPP_TIMEOUT):

        self.__enforce_no_existing_ppp_session()

        result = self._ppp.connect(timeout=timeout)

        if result == True:
            if not self.route.wait_for_interface(DEFAULT_PPP_INTERFACE,
                                   MAX_PPP_INTERFACE_UP_RETRIES):
                self.logger.error('Unable to find interface %s. Disconnecting',
                        DEFAULT_PPP_INTERFACE)
                self._ppp.disconnect()
                return False
            return True
        else:
            return False


    def disconnect(self):
        self._ppp.disconnect()
        self.__shut_down_existing_ppp_session()
        return True

    # EFFECTS: Makes sure that there are no existing PPP instances on the same
    #          device interface.
    def __enforce_no_existing_ppp_session(self):

        pid_list = self.__check_for_existing_ppp_sessions()

        if len(pid_list) > 0:
            raise PPPError('Existing PPP session(s) are established by pid(s) %s. Please close/kill these processes first'
                             % pid_list)

    def __shut_down_existing_ppp_session(self):
        pid_list = self.__check_for_existing_ppp_sessions()

        # Process this only if it is a valid PID integer.
        for pid in pid_list:
            self.logger.info('Killing pid %s that currently have an active PPP session',
                             pid)
            psutil.Process(pid).terminate()

    def __check_for_existing_ppp_sessions(self):

        existing_ppp_pids = []
        self.logger.info('Checking for existing PPP sessions')

        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name'])
            except:
                raise PPPError('Failed to check for existing PPP sessions')

            if 'pppd' in pinfo['name']:
                self.logger.info('Found existing PPP session on pid: %s', pinfo['pid'])
                existing_ppp_pids.append(pinfo['pid'])

        return existing_ppp_pids

    @property
    def localIPAddress(self):
        return self._ppp.raddr

    @property
    def remoteIPAddress(self):
        return self._ppp.laddr
