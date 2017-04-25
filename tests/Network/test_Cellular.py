import sys
import pytest

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Network import Cellular

class TestCellular(object):

    def test_invalid_cellular_type(self):
        with pytest.raises(Exception, message = 'Invalid modem type: invalidmodem'):
            cellular = Cellular.Cellular('invalidmodem')
