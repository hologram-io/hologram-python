from HologramCloud import HologramCloud
from Raw import Raw
from Network import Wifi
from Network import Ethernet
from Network import BLE
from Network import Cellular
from Network import NonNetwork
from Authentication import *

version = '0.1.0'

class Hologram(object):

    _networkHandlers =  {
        '' : NonNetwork.NonNetwork,
        'wifi' : Wifi.Wifi,
        'cellular': Cellular.Cellular,
        'ble' : BLE.BLE,
        'ethernet' : Ethernet.Ethernet,
        }

    _messageModeHandlers = {
        'tcp-other' : Raw,
        'hologram_cloud' : HologramCloud,
        }

    _authenticationHandlers = {
        'csrpsk' : CSRPSKAuthentication.CSRPSKAuthentication,
        'totp' : TOTPAuthentication.TOTPAuthentication,
        }

    def __init__(self, credentials, network = '', message_mode = 'hologram_cloud',
                 authentication = 'csrpsk'):

        self.credentials = credentials

        # Authentication Configuration
        self.authentication = authentication

        # Raw/Cloud Configuration
        self.message_mode = message_mode

        # Network Configuration
        self.network = network

    @property
    def network(self):
        return self._network

    @network.setter
    def network(self, network):
        if network not in Hologram._networkHandlers:
            raise Exception('Invalid network type: %s' % network)

        self._network = Hologram._networkHandlers[network]()

    @property
    def message_mode(self):
        return self._message_mode

    @message_mode.setter
    def message_mode(self, mode):

        if mode not in Hologram._messageModeHandlers:
            raise Exception('Invalid message_mode type: %s' % mode)

        self._message_mode = Hologram._messageModeHandlers[mode](self.authentication)

    @property
    def authentication(self):
        return self._authentication

    @authentication.setter
    def authentication(self, authentication):
        if authentication not in Hologram._authenticationHandlers:
            raise Exception('Invalid authentication type: %s' % authentication)

        self._authentication = Hologram._authenticationHandlers[authentication](self.credentials)

    def getSDKVersion(self):
        return version

    def sendMessage(self, messages, topics = None):
        return self._message_mode.sendMessage(messages, topics)

    # EFFECTS: Sends the SMS to the destination number specified.
    def sendSMS(self, destination_number, message):
        return self._message_mode.sendSMS(destination_number, message)

    @property
    def send_host(self):
        return self._message_mode.send_host

    @send_host.setter
    def send_host(self, send_host):
        self._message_mode.send_host = send_host

    @property
    def send_port(self):
        return self._message_mode.send_port

    @send_port.setter
    def send_port(self, send_port):
        self._message_mode.send_port = send_port

    @property
    def event(self):
        return self._message_mode.event

    @event.setter
    def event(self, event):
        self._message_mode.event = event

