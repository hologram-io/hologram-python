import sys

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network.Modem import E303

class TestE303(object):

    def test_Modem_create(self):
        modem = E303.E303()
