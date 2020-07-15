import sys

sys.path.append(".")
sys.path.append("..")
from Hologram.Modem import Modem
from Hologram.Utils import ModemResult


class MockModem(Modem):
    def __init__(self):
        # dont init super class
        self.device_name = 'Mock Modem'
        self.baud_rate = 9600

        self.serial_port = '/dev/ttyUSB0'
        self.timeout = Modem.DEFAULT_SERIAL_TIMEOUT
        self.response = []
        self._at_sockets_available = False
        self.urc_state = Modem.SOCKET_INIT
        self.socket_identifier = 0
        self.last_read_payload_length = 0
        self.result = ModemResult.OK
        self.debug_out = ''
        self.in_ext = False