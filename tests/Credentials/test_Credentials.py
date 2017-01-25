import sys
import pytest

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Credentials import Credentials


class TestCredentials(object):

    def test_create(self):
        CSRPSKID = '1234'
        CSRPSKKey = '5678'

        credentials = Credentials(CSRPSKID, CSRPSKKey)

        assert credentials.cloud_id == '1234'
        assert credentials.cloud_key == '5678'

    def test_create_empty_cloud_id_and_key(self):
        credentials = Credentials()
        assert credentials.cloud_id == ''
        assert credentials.cloud_key == ''

    def test_create_long_invalid_cloud_id(self):
        CSRPSKID = '1234567890'
        CSRPSKKey = '1234'

        with pytest.raises(ValueError, message = 'cloud_id must be 4 characters long'):
            credentials = Credentials(CSRPSKID, CSRPSKKey)

    def test_create_long_invalid_cloud_key(self):
        CSRPSKID = '1234'
        CSRPSKKey = '1234567890'

        with pytest.raises(ValueError, message = 'cloud_key must be 4 characters long'):
            credentials = Credentials(CSRPSKID, CSRPSKKey)