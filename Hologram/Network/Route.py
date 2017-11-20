# Route.py - Hologram Python SDK Routing Manager
#            This module configures routing for Hologram SDK.
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

import logging
import time
from logging import NullHandler
from pyroute2 import IPRoute
from pyroute2.netlink.exceptions import NetlinkError

DEFAULT_DESTINATION = '0.0.0.0/0'


class Route(object):
    def __init__(self):
        self.ipr = IPRoute()
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(NullHandler())

    def is_interface_available(self, interface):
        # An interface is considered available if it is simply on the ip route list.
        # The interface does not need to be UP in order to be considered available.
        return self.__interface_index(interface) is not None

    def wait_for_interface(self, interface, max_retries):
        count = 0
        while count <= max_retries:
            try:
                # Check if ready to break out of loop when interface is found.
                if self.is_interface_available(interface):
                    # NOTE: Ideally this conditional would be based on
                    #       self.is_interface_up(interface), but there is an issue
                    #       where the state of a ppp0 interface may show UNKNOWN
                    #       on Raspbian linux even if ppp0 is UP.
                    return True
                else:
                    self.logger.info('Waiting for interface %s:', interface)
                    time.sleep(1)
                    count += 1
            except Exception as e:
                pass
        if count > max_retries:
            return False

    def add_default(self, gateway):
        try:
            self.add(DEFAULT_DESTINATION, gateway)
        except NetlinkError as e:
            self.logger.debug('Could not set default route due to NetlinkError: %s', str(e))

    def add(self, destination, gateway):
        self.ipr.route('add',
                       dst=destination,
                       gateway=gateway)

    def __interface_index(self, interface):
        index = None
        indexes = self.ipr.link_lookup(ifname=interface)
        if len(indexes) == 1:
            index = indexes[0]
        return index

    def __get_interface_state(self, interface):
        if self.is_interface_available(interface):
            link_state = None
            ipr_index = self.__interface_index(interface)
            links = self.ipr.get_links()

            for link in links:
                if link['index'] == ipr_index:
                    link_state = link.get_attr('IFLA_OPERSTATE')
                    break
            return link_state
        else:
            return None
