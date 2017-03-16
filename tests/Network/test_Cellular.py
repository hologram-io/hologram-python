import sys
import pytest

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network import Cellular

class TestCellular(object):

    def test_cellular_e303_create(self):
        cellular = Cellular.Cellular('e303')
        assert repr(cellular.modem) == 'E303'

    def test_cellular_ms2131_create(self):
        cellular = Cellular.Cellular('ms2131')
        assert repr(cellular.modem) == 'MS2131'

    def test_cellular_iota_create(self):
        cellular = Cellular.Cellular('iota')
        assert repr(cellular.modem) == 'IOTA'

    def test_invalid_cellular_type(self):
        with pytest.raises(Exception, message = 'Invalid modem type: invalidmodem'):
            cellular = Cellular.Cellular('invalidmodem')
