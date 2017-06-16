# hologram-python

[![PyPI version](https://badge.fury.io/py/hologram-python.svg)](https://badge.fury.io/py/hologram-python)

[![Build Status](https://travis-ci.org/hologram-io/hologram-python.svg?branch=master)](https://travis-ci.org/hologram-io/hologram-python)

## Introduction
This is a Python SDK that allows you to send messages to either your or our cloud.

You can also send SMS via our cloud services to a given destination number of your choice!

We understand that you may run this library in smaller, more power constraint devices.
In the spirit of bringing connectivity to your devices, we also provided you with
many popular networking interfaces such as WiFi and Cellular services, which you can
choose within this SDK.

## Installation

### Requirements:

You will need `ppp` and Python 2.7 installed on your system for the SDK to work.

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
