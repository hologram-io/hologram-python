# hologram-python

[![PyPI version](https://badge.fury.io/py/hologram-python.svg)](https://badge.fury.io/py/hologram-python)

[![Build Status](https://travis-ci.org/hologram-io/hologram-python.svg?branch=master)](https://travis-ci.org/hologram-io/hologram-python)

## Introduction
The Hologram Python Device SDK provides a simple way for devices to connect 
and communicate with the Hologram or other IoT platforms.  You can activate, provision, 
send messages, receive inbound access connections, send/receive SMS, and 
setup secure tunnels.

The SDK also supports networking interfaces for WiFi in addition to Cellular 
in the spirit of bringing connectivity to your devices.

## Installation

### Requirements:

You will need `ppp` and Python 3.7 installed on your system for the SDK to work.

We wrote scripts to ease the installation process.

Please run this command to download the script that installs the Python SDK:

`curl -L hologram.io/python-install | bash`

Please run this command to download the script that updates the Python SDK:

`curl -L hologram.io/python-update | bash`

If everything goes well, you’re done and ready to use the SDK.

## Directory Structure

1. `tests` - This contains many of Hologram SDK unit tests.
2. `scripts` -  This directory contains example Python scripts that utilize the Python SDK.
3. `Hologram` - This directory contains all the Hologram class interfaces.
4. `Exceptions` - This directory stores our custom `Exception` used in the SDK.

You can also find more documentation [here](https://hologram.io/docs/reference/cloud/python-sdk).

## Support
Please feel free to [reach out to us](mailto:support@hologram.io) if you have any questions/concerns.
