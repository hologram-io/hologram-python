import sys

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network import Wifi

class TestWifi(object):

    def test_Wifi(self):
        wifi = Wifi.Wifi()
        assert wifi.interfaceName == 'wlan0'

        wifi.interfaceName = 'wlan1'
        assert wifi.interfaceName == 'wlan1'

    def test_Wifi_with_specified_interface(self):

        wifi = Wifi.Wifi(interfaceName = 'wlan2')
        assert wifi.interfaceName == 'wlan2'
