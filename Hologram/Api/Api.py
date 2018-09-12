# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# Api.py - This file contains the Hologram REST API class implementation.

from Exceptions.HologramError import ApiError

import logging
from logging import NullHandler
import requests

HOLOGRAM_REST_API_BASEURL = 'https://dashboard.hologram.io/api/1'

class Api(object):

    def __init__(self, apikey='', username='', password=''):
        # Logging setup.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(NullHandler())
        self.authtype = None

        self.__enforce_auth_method(apikey, username, password)

        self.apikey = apikey
        self.username = username
        self.password = password

    # REQUIRES: a SIM number and a plan id.
    # EFFECTS: Activates a SIM. Returns a tuple of a success flag and
    #          more info about the response.
    def activateSIM(self, sim='', plan=None, zone=1, preview=False):

        endpoint = HOLOGRAM_REST_API_BASEURL + '/links/cellular/sim_' + str(sim) + '/claim'

        args = self.__populate_auth_payload()
        args['data'] = {'plan': plan, 'tier': zone}

        if preview == True:
            args['params']['preview'] = 1

        response = requests.post(endpoint, **args)
        if response.status_code != requests.codes.ok:
            return (False, response.text)

        response = response.json()
        if response['success'] == False:
            return (response['success'], response['data'][str(sim)])
        return (response['success'], response['order_data'])

    # EFFECTS: Returns a list of plans. Returns a tuple of a success flag and
    #          more info about the response.
    def getPlans(self):
        endpoint = HOLOGRAM_REST_API_BASEURL + '/plans'
        args = self.__populate_auth_payload()

        response = requests.get(endpoint, **args)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()

        response = response.json()
        return (response['success'], response['data'])

    # EFFECTS: Gets the SIM state
    def getSIMState(self, sim):
        endpoint = HOLOGRAM_REST_API_BASEURL + '/links/cellular'

        args = self.__populate_auth_payload()
        args['params']['sim'] = str(sim)

        response = requests.get(endpoint, **args)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()

        response = response.json()
        return (response['success'], response['data'][0]['state'])

    # EFFECTS: Populates and returns a dictionary with the proper HTTP
    #          authentication credentials.
    def __populate_auth_payload(self):

        args = dict()
        args['params'] = dict()

        if self.authtype == 'basic_auth':
            args['auth'] = (self.username, self.password)
        elif self.authtype == 'apikey':
            args['params'] = {'apikey' : self.apikey}
        else:
            raise ApiError('Invalid HTTP Authentication type')

        return args

    # EFFECTS: Checks to make sure that the valid authentication parameters are being used
    #          correctly, throws an Exception if there's an issue with it.
    def __enforce_auth_method(self, apikey, username, password):
        if apikey == '' and (username == '' or password == ''):
            raise ApiError('Must specify valid HTTP authentication credentials')
        elif apikey == '':
            self.authtype = 'basic_auth'
        else:
            self.authtype = 'apikey'
