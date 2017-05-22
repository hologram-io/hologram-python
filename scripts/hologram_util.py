import time

def handle_timeout(timeout):
    if timeout != -1:
        print 'waiting for ' + str(timeout) + ' seconds...'
        time.sleep(timeout)
    else:
        while True:
            time.sleep(1)
