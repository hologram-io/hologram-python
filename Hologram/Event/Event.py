# Event.py - Hologram Python SDK Event interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License

class Event(object):
    _funcLookupTable = {}
    def __init__(self):
        self.__dict__ = self._funcLookupTable

    def subscribe(self, event, callback):

        if not self.__dict__.get(event):
            self.__dict__[event] = [callback]
        else:
            self.__dict__[event].append(callback)

    def unsubscribe(self, event, callback):

        if not self.__dict__.get(event):
            return

        # Iterate over the list of callbacks and remove the specified one.
        for temp in self.__dict__[event][:]:
            if temp is callback:
                self.__dict__[event].remove(temp)

    # EFFECTS: Broadcasts the triggered event to all subscribers.
    def broadcast(self, event):

        callbacks = self.__dict__.get(event)

        if callbacks:
            for callback in callbacks:
                callback()
