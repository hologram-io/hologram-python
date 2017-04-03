#!/usr/bin/env python
# Copyright 2016 Hologram (Konekt, Inc.)
#
# Author: Hologram <support@hologram.io>
#

longdesc = '''
This is a library for connecting to the Hologram Cloud
'''

import sys
try:
    from setuptools import setup, find_packages
    kw = {
    }
except ImportError:
    from distutils.core import setup
    kw = {}

if sys.platform == 'darwin':
    import setup_helper
    setup_helper.install_custom_make_tarball()

version = '0.4.0'

setup(
    name = 'hologram-python',
    version = version,
    description = 'Library for accessing Hologram Cloud at https://hologram.io',
    long_description = longdesc,
    author = 'Hologram',
    author_email = 'support@hologram.io',
    url = 'https://github.com/hologram-io/hologram-python/',
    packages = find_packages(),
    include_package_data = True,
    install_requires = open('requirements.txt').read().split(),
    scripts = ['scripts/hologram_send', 'scripts/hologram_sms',
               'scripts/hologram_receive', 'scripts/cellular_receive',
               'scripts/iota_receive', 'scripts/e303_receive',
               'scripts/ms2131_receive'],
    license = 'MIT',
    platforms = 'Posix; MacOS X; Windows',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet',
        'Topic :: Security :: Cryptography',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    **kw
)
