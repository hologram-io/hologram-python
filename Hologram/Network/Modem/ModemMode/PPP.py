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
from pppd import PPPConnection
from IPPP import IPPP

DEFAULT_PPP_TIMEOUT = 200

class PPP(IPPP):

    def __init__(self, device_name='/dev/ttyUSB0', baud_rate='9600',
                 chatscript_file=None):

        super(PPP, self).__init__(device_name=device_name, baud_rate=baud_rate,
                                  chatscript_file=chatscript_file)

        self._ppp = PPPConnection(self.device_name, self.baud_rate, 'noipdefault',
                                  'usepeerdns', 'defaultroute', 'persist', 'noauth',
                                  connect=self.connect_script)

    def isConnected(self):
        return self._ppp.connected()

    # EFFECTS: Establishes a PPP connection. If this is successful, it will also
    #          reroute packets to ppp0 interface.
    def connect(self, timeout=DEFAULT_PPP_TIMEOUT):
        result = self._ppp.connect(timeout=timeout)

        if result == True:
            self.__reroute_packets()
        return result

    def disconnect(self):
        return self._ppp.disconnect()

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
