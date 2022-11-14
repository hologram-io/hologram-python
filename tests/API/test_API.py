import sys
import pytest
from unittest.mock import Mock, patch
sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Api import Api
from Exceptions.HologramError import ApiError

class TestHologramAPI:

    def test_create_no_creds(self):
        with pytest.raises(ApiError, match = 'Must specify valid HTTP authentication credentials'):
            Api()

    def test_create_missing_password(self):
        with pytest.raises(ApiError, match = 'Must specify valid HTTP authentication credentials'):
            Api(username='user')

    def test_create_missing_username(self):
        with pytest.raises(ApiError, match = 'Must specify valid HTTP authentication credentials'):
            Api(password='password')

    @patch('requests.post')
    def test_activate(self, r_post):
        api = Api(apikey='123apikey')
        
        r_post.return_value = Mock(status_code=200)
        r_post.return_value.json = Mock(return_value={"success": True, 'order_data': {}})
        
        success, response = api.activateSIM('iccid')

        assert success == True
        assert response == {}

    @patch('requests.post')
    def test_activate_failed(self, r_post):
        api = Api(apikey='123apikey')
        
        r_post.return_value = Mock(status_code=200)
        r_post.return_value.json = Mock(return_value={"success": False, 'data': {'iccid': 'Activation failed'}})
        
        success, response = api.activateSIM('iccid')

        assert success == False
        assert response == 'Activation failed'

    @patch('requests.post')
    def test_activate_bad_status_code(self, r_post):
        api = Api(apikey='123apikey')
        
        r_post.return_value = Mock(
            status_code=429,
            text = 'Too many requests')
        
        success, response = api.activateSIM('iccid')

        assert success == False
        assert response == 'Too many requests'

    @patch('requests.get')
    def test_get_plans(self, r_post):
        api = Api(apikey='123apikey')
        
        r_post.return_value.json = Mock(return_value={"success": True, 'data': {'id': 1, 'orgid': 1}})
        
        success, response = api.getPlans()

        assert success == True
        assert response == {'id': 1, 'orgid': 1}

    @patch('requests.get')
    def test_get_sim_state(self, r_post):
        api = Api(apikey='123apikey')
        
        r_post.return_value.json = Mock(return_value={"success": True, 'data': [{'state': 'LIVE'}]})
        
        success, response = api.getSIMState('iccid')

        assert success == True
        assert response == 'LIVE'

