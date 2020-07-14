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
from Hologram.PPP.pppd import PPPConnection
from Hologram.PPP import IPPP
from Hologram.Util.Route import Route
from Hologram.Exceptions.HologramError import PPPError

DEFAULT_PPP_TIMEOUT = 200
DEFAULT_PPP_INTERFACE = 'ppp0'
MAX_PPP_INTERFACE_UP_RETRIES = 10
MAX_REROUTE_PACKET_RETRIES = 15


class PPP(IPPP):

    def __init__(self, device_name='/dev/ttyUSB0', all_attached_device_names=[],
                 baud_rate='9600', chatscript_file=None):

        super().__init__(device_name=device_name, baud_rate=baud_rate,
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

        if result :
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
        PPP.shut_down_existing_ppp_session(self.logger)
        return True

    # EFFECTS: Makes sure that there are no existing PPP instances on the same
    #          device interface.
    def __enforce_no_existing_ppp_session(self):

        pid_list = PPP.check_for_existing_ppp_sessions(self.logger)

        if len(pid_list) > 0:
            raise PPPError('Existing PPP session(s) are established by pid(s) %s. Please close/kill these processes first'
                           % pid_list)

    @staticmethod
    def shut_down_existing_ppp_session(logger):
        pid_list = PPP.check_for_existing_ppp_sessions(logger)

        # Process this only if it is a valid PID integer.
        for pid in pid_list:
            logger.info('Killing pid %s that currently have an active PPP session',
                             pid)
            process = psutil.Process(pid)
            process.terminate()
            # Wait at least 10 seconds for the process to terminate
            process.wait(10)

    @staticmethod
    def check_for_existing_ppp_sessions(logger):

        existing_ppp_pids = []
        logger.info('Checking for existing PPP sessions')

        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name'])
            except:
                raise PPPError('Failed to check for existing PPP sessions')

            if 'pppd' in pinfo['name']:
                logger.info('Found existing PPP session on pid: %s', pinfo['pid'])
                existing_ppp_pids.append(pinfo['pid'])

        return existing_ppp_pids

    @property
    def localIPAddress(self):
        return self._ppp.raddr

    @property
    def remoteIPAddress(self):
        return self._ppp.laddr
