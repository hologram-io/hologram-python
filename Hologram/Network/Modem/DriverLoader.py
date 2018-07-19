# DriverLoader.py - Class that wraps around different module loading
# operations that are used for the R410 and maybe other modems in the
# future
# Author: Hologram <support@hologram.io>
#
#
# Copyright 2018 - Hologram (Konekt, Inc.)
#
#
# LICENSE: Distributed under the terms of the MIT License
#

import subprocess


class DriverLoader(object):
    # I would much rather use python-kmod for all this
    # but it doesn't seem to build properly on the Pi and
    # hasn't been updated in years. It's possible we need to update
    # to python 3 for it to work correctly


    def is_module_loaded(self, module):
        output = subprocess.check_output(['lsmod'])
        lines = output.splitlines()
        for line in lines:
            splitline = line.split()
            if splitline[0] == "option":
                return True
        return False


    def load_module(self, module):
        subprocess.call(['sudo', 'modprobe', module])


    def force_driver_for_device(self, syspath, vid, pid):
        with open(syspath, "w") as f:
            f.write("%s %s"%(vid, pid))





