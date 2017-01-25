# Credentials.py - Hologram Python SDK Network interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)

# This Credentials file contains the major config keys/settings that are required
# by some of the networking + authentication interfaces.
#
# LICENSE: Distributed under the terms of the MIT License
#
class Credentials(object):

    def __init__(self, cloud_id = '', cloud_key = '', device_id = '',
                 private_key = ''):
        self.cloud_id = cloud_id
        self.cloud_key = cloud_key
        self.device_id = device_id
        self.private_key = private_key

    @property
    def cloud_id(self):
        return self._cloud_id

    @cloud_id.setter
    def cloud_id(self, cloud_id):

        if len(cloud_id) == 4 or len(cloud_id) == 0:
            self._cloud_id = cloud_id
        else:
            raise ValueError('cloud_id must be 4 characters long')

    @property
    def cloud_key(self):
        return self._cloud_key

    @cloud_key.setter
    def cloud_key(self, cloud_key):

        if len(cloud_key) == 4 or len(cloud_key) == 0:
            self._cloud_key = cloud_key
        else:
            raise ValueError('cloud_key must be 4 characters long')

    @property
    def device_id(self):
        return self._device_id

    @device_id.setter
    def device_id(self, deviceid):
        self._device_id = deviceid

    @property
    def private_key(self):
        return self._private_key

    @private_key.setter
    def private_key(self, private_key):
        self._private_key = private_key


