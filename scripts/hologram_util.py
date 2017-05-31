import time
import sys

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
