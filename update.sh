#!/bin/bash
# Author: Hologram <support@hologram.io>
#
# Copyright 2016 - Hologram (Konekt, Inc.)
#
# LICENSE: Distributed under the terms of the MIT License
#
# update.sh - This file helps update this Python SDK and all required dependencies
#              on a machine.

set -euo pipefail

sudo apt-get install libpython2.7-dev

sudo pip install hologram-python --upgrade
