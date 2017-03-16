import sys

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network.Modem import MS2131

class TestMS2131(object):

    def test_Modem_create(self):
        modem = MS2131.MS2131()
