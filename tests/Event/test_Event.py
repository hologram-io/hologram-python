import sys

sys.path.append(".")
sys.path.append("..")
sys.path.append("../..")
from Hologram.Event import Event

class TestEvent(object):

    def test_create(self):
        event = Event()
