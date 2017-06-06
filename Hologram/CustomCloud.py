# CustomCloud.py - Hologram Python SDK Custom Cloud interface
#
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License

from collections import deque
import socket
import sys
import threading
import time
from Cloud import Cloud
from Exceptions.HologramError import HologramError

MAX_QUEUED_CONNECTIONS = 5
RECEIVE_TIMEOUT = 5
MIN_PERIODIC_INTERVAL = 10

class CustomCloud(Cloud):

    def __init__(self, credentials, send_host='', send_port=0,
                 receive_host='', receive_port=0, enable_inbound=False,
                 network=''):

        # Enforce that the send and receive configs are set before using the class.
        if enable_inbound and (receive_host == '' or receive_port == 0):
            raise Exception('Must set receive host and port for inbound connection')

        super(CustomCloud, self).__init__(credentials,
                                          send_host=send_host,
                                          send_port=send_port,
                                          receive_host=receive_host,
                                          receive_port=receive_port,
                                          network=network)

        self._periodic_msg_lock = threading.Lock()
        self._periodic_msg = None
        self._periodic_msg_enabled = False

        self._receive_buffer_lock = threading.Lock()
        self._receive_cv = threading.Lock()
        self._receive_buffer = deque()
        self._receive_socket = None

        self._accept_thread = None
        self.socketClose = True

        if enable_inbound == True:
            self.initializeReceiveSocket()

    # EFFECTS: Sends the message to the cloud.
    def sendMessage(self, message, timeout=5):

        try:
            self.__enforce_send_host_and_port()

            if not self._networkManager.networkActive:
                self.addPayloadToBuffer(message)
                return ''

            self.logger.info("Connecting to: %s", self.send_host)
            self.logger.info("%s", self.send_port)

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((self.send_host, self.send_port))

            self.logger.info("Sending message of length %d...", len(message))
            self.logger.debug('Send: ')

            self.logger.debug(message)

            sock.send(message)

            self.logger.info('Sent.')

            resultbuf = ''
            while True:
                try:
                    result = sock.recv(1024)
                except socket.timeout:
                    break
                if not result:
                    break
                resultbuf += result

            try:
                sock.shutdown(socket.SHUT_RDWR)
            except socket.error:
                pass

            sock.close()
            self.logger.info('Socket closed.')

            self.event.broadcast('message.sent')
            return resultbuf

        except HologramError as e:
            self.logger.error(repr(e))
            sys.exit(1)
        except (IOError):
            self.logger.error('An error occurred while attempting to send the message to the cloud')
            self.logger.error('Please try again.')
            return ''

    # REQUIRES: The interval in seconds, message body, optional topic(s) and a timeout value
    #           for how long in seconds before the socket is closed.
    # EFFECTS: Sends asychronous periodic messages every interval seconds.
    def sendPeriodicMessage(self, interval, message, topics=None, timeout=5):

        try:
            self._enforce_minimum_periodic_interval(interval)
        except HologramError as e:
            self.logger.error(repr(e))
            sys.exit(1)

        self._periodic_msg_lock.acquire()

        if self._periodic_msg_enabled == True:
            raise Exception('Cannot have more than 1 periodic message job at once')

        self._periodic_msg_enabled = True

        self._periodic_msg_lock.release()

        self._periodic_msg = threading.Thread(target=self._periodic_job_thread,
                                              args=[interval, self.sendMessage,
                                                    message, topics, timeout])
        self._periodic_msg.daemon = True
        self._periodic_msg.start()

    def sendSMS(self, destination_number, message):
        raise NotImplementedError('Cannot send SMS via custom cloud')

    # EFFECTS: This threaded infinite loop shoud keep sending messages with the specified
    #          interval.
    def _periodic_job_thread(self, interval, function, *args):

        while True:
            self._periodic_msg_lock.acquire()

            if not self._periodic_msg_enabled:
                self._periodic_msg_lock.release()
                break

            self.logger.info('Sending another periodic message...')
            response = function(*args)
            self.logger.info('DATA RECEIVED: ' +  str(response))

            self._periodic_msg_lock.release()
            time.sleep(interval)

    def stopPeriodicMessage(self):
        self.logger.info('Stopping periodic job...')

        self._periodic_msg_lock.acquire()
        self._periodic_msg_enabled = False
        self._periodic_msg_lock.release()

        self._periodic_msg.join()
        self.logger.info('Periodic job stopped')

    def initializeReceiveSocket(self):

        try:
            self.__enforce_receive_host_and_port()
        except HologramError as e:
            self.logger.error(repr(e))
            sys.exit(1)

        self._receive_cv.acquire()
        self._receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.logger.info('Socket created')
        self._receive_cv.release()

        self.openReceiveSocket()

        return True

    # EFFECTS: Opens and binds an inbound socket connection.
    def openReceiveSocket(self):

        self._receive_cv.acquire()

        # Try to bind to the socket if it's already initialized.
        try:
            self.logger.info('Binding to socket...')
            self._receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._receive_socket.bind((self.receive_host, self.receive_port))
        except socket.error:
            self.logger.info('Retrying...')
            try:
                self._receive_socket.shutdown(socket.SHUT_RDWR)
            except socket.error:
                pass
            self._receive_socket.close()
            self._receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._receive_socket.bind((self.receive_host, self.receive_port))

        # Set socketClose back to False since we're opening it again.
        self.socketClose = False

        # become a server socket
        self._receive_socket.listen(MAX_QUEUED_CONNECTIONS)
        self._receive_cv.release()

        # Spin a new thread for accepting incoming operations
        self._accept_thread = threading.Thread(target = self.acceptIncomingConnection)
        self._accept_thread.daemon = True
        self._accept_thread.start()

    # EFFECTS: Closes the inbound socket connection.
    def closeReceiveSocket(self):

        self._receive_cv.acquire()

        self.logger.info('Closing socket...')

        self.socketClose = True
        self._receive_cv.release()

        self._accept_thread.join()

        self._receive_cv.acquire()
        try:
            self._receive_socket.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass

        self._receive_socket.close()
        self.logger.info('Socket closed.')

        self._receive_cv.release()

    def acceptIncomingConnection(self):
        # This threaded infinite loop shoud keep listening on an incoming connection
        while True:
            self._receive_cv.acquire()

            if self.socketClose:
                self._receive_cv.release()
                break

            try:
                self._receive_socket.setblocking(0)
                (clientsocket, address) = self._receive_socket.accept()
                self.logger.info('Connected to ' + str(address))
                # Spin a new thread to handle the current incoming operation.
                threading.Thread(target = self.__incoming_connection_thread,
                                 args = [clientsocket]).start()
            except:
                pass

            self._receive_cv.release()

    # EFFECTS: This threaded method accepts an inbound connection and appends
    #          the received message onto the receive buffer.
    #          It also broadcasts the message.received event
    def __incoming_connection_thread(self, clientsocket):

        clientsocket.settimeout(RECEIVE_TIMEOUT)

        # Keep parsing the received data until timeout or receive no more data.
        recv = ''
        while True:
            try:
                result = clientsocket.recv(1024)
            except socket.timeout:
                break
            if not result:
                break
            recv += result

        self.logger.info('Received message: ' + str(recv))

        self._receive_buffer_lock.acquire()

        # Append received message into receive buffer
        self._receive_buffer.append(recv)
        self.logger.debug('Receive buffer: ' + str(self._receive_buffer))

        self._receive_buffer_lock.release()

        self.event.broadcast('message.received')
        clientsocket.close()

    # EFFECTS: Returns the receive buffer and empties it.
    def popReceivedMessage(self):
        self._receive_buffer_lock.acquire()

        if len(self._receive_buffer) == 0:
            data = None
        else:
            data = self._receive_buffer.popleft()

        self._receive_buffer_lock.release()
        return data

    # EFFECTS: Makes sure that the send host and port are set before making
    #          outbound connection.
    def __enforce_send_host_and_port(self):
        if self.send_host == '' or self.send_port == 0:
            raise HologramError('Send host and port must be set before making this operation')

    # EFFECTS: Makes sure that the receive host and port are set before making
    #          an inbound connection.
    def __enforce_receive_host_and_port(self):
        if self.receive_host == '' or self.receive_port == 0:
            raise HologramError('Receive host and port must be set before making this operation')

    def _enforce_minimum_periodic_interval(self, interval):
        if interval < MIN_PERIODIC_INTERVAL:
            raise HologramError('Interval cannot be less than %d seconds.' % MIN_PERIODIC_INTERVAL)
