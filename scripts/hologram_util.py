import time
import sys

DEFAULT_DELAY_INTERVAL = 0

def handle_timeout(timeout):

    try:
        if timeout != -1:
            print 'waiting for ' + str(timeout) + ' seconds...'
            time.sleep(timeout)
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt as e:
        sys.exit(e)

def handle_polling(timeout, fx, delay_interval=DEFAULT_DELAY_INTERVAL):
    try:
        if timeout != -1:
            print 'waiting for ' + str(timeout) + ' seconds...'
            end = time.time() + timeout
            while time.time() < end:
                fx()
                time.sleep(delay_interval)
        else:
            while True:
                fx()
                time.sleep(delay_interval)
    except KeyboardInterrupt as e:
        sys.exit(e)
