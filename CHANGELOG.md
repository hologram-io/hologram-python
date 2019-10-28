# What's New in Hologram Python SDK

## v0.9.0
2019-10-28 Hologram <support@hologram.io>
    * Converted SDK to use Python 3. This version is compatible with Python 3 only
        and drops support for Python 2. There are no changes to any features or
        interfaces in this release. Functionality should mirror v0.8.3 but will now
        run on Python 3

## v0.8.3

2019-08-27 Hologram <support@hologram.io>
    * New command to view IMEI: `hologram modem imei`
    * New command to get modem module firmware version: `hologram modem version`
    * Make dependencies a little more flexible to prevent some problems on some systems
    * Unit tests weren't properly checking some exceptions

## v0.8.2

2018-11-16 Hologram <support@hologram.io>
    * Added new commands to control cellular radio: `hologram modem radio-off`
        and `hologram modem radio-on`
    * Added new command to restart the modem: `hologram modem reset`
    * Deprecated `hologram modem connect` and `hologram modem disconnect` in
        favor of the network versions of those commands. They'll be removed
        in a future release
    * Fix issue with auto periodic message sending taking a long time to stop
        when killed
    * Fix issue where `hologram network connect` would print that it worked
        even when it didn't
    * Fix issue where a zombie pppd process would hang around in the background
        after a connection failure and tie up a serial port
    * General code cleanup around the PPP path

## v0.8.1

2018-09-12 Hologram <support@hologram.io>
    * Fix issues with PPP (`hologram network connect`) on Nova R410
    * Fix bugs with activating SIM cards via `hologram activate`
        command and stop echoing out passwords

## v0.8.0

2018-07-19 Hologram <support@hologram.io>
    * Add support for Nova R410 Cat-M modem
    * Drivers for R410 and R404 are loaded automatically
    * Revamp error handling on AT command connect so we don't keep
        moving the process forward if we've already failed
    * Fixes to the repeated message send feature

## v0.7.6

2018-04-04 Hologram <support@hologram.io>
    * hologram receive reconnects after forced disconnect
    * Replace usb dependency with cross platform library

## v0.7.5

2018-02-13 Hologram <support@hologram.io>
    * Force persistent connection for hologram spacebridge
    * hologram spacebridge no longer sets default route
    * Remove redundant manifest includes

2018-02-06 Hologram <support@hologram.io>
    * Increase socket connect and write timeouts

2018-02-05 Hologram <support@hologram.io>
    * Fix infinite loop in `send_message`

## v0.7.4

2018-01-08 Hologram <support@hologram.io>
    * Just a bunch of internal tool changes. Happy New Year! :)

## v0.7.3

2018-01-04 Hologram <support@hologram.io>
    * Just a bunch of internal tool changes. Happy New Year! :)

## v0.7.2

2017-12-18 Hologram <support@hologram.io>
    * Removed `testAll` from Makefile. All unit tests will now run even if uid isn't root.

2017-11-30 Hologram <support@hologram.io>
    * Refactored unit tests for Modem and MS2131 classes.

2017-12-07 Hologram <support@hologram.io>
    * Refactored Nova <-> Nova u201 interface.

2017-12-05 Hologram <support@hologram.io>
    * Added open source headers to SDK source files

2017-12-01 Hologram <support@hologram.io>
    * Added `ERR_TOPICINVALID` and `ERR_METADATAINVALID` error codes to HologramCloud

2017-11-30 Hologram <support@hologram.io>
    * converted ChangeLog into a markdown file and added release tags to it

## v0.7.1

2017-11-29 Hologram <support@hologram.io>
    * Disregard extra responses in Modem::check_registed()
    * Fixed Nova R404 `.connect()` / `.disconnect()` regressions.

## v0.7.0

2017-11-20 Hologram <support@hologram.io>
    * Added modem is_connected interface. Checks for when a message/SMS can be sent.
    * Cleaned up example scripts.
    * Fixed misleading 'unable to receive device_id and private_key error'
    * Fixed unkilled PPP sessin after specified timeout.
    * Fixed misleading error log when users call `hologram activate`
    * Updated requirements.txt to point to python-sdk-auth v0.2.0
    * Removed TOTP Auth mode option for SMS sends
    * Catch NetlinkErorr if setting default route fails
    * Add overloaded close_socket interface for R404 listening feature
    * Cleaned up redundant scripts within the `examples/` folder

2017-10-24 Hologram <support@hologram.io>
    * Added modem is_connected interface. Checks for when a message/SMS can be sent.
    * Cleaned up example scripts.

2017-10-23 Hologram <support@hologram.io>
    * Added hologram network connect/disconnect CLI commands, deprecating
      modem connect/disconnect soon.
    * Writes/reads on AT command sockets are now done in hex mode.
    * Fix regression where a receive SMS CLI keyboard interrupt will print a
      stack trace.

2017-10-20 Hologram <support@hologram.io>
    * Sends/receives are done via AT sockets by default instead of a PPP session.

## v0.6.1

2017-09-29 Hologram <support@hologram.io>
    * Fixed bug where empty result list might cause an index error

2017-09-28 Hologram <support@hologram.io>
    * Logging is now turned off by default for CLI subcommands.
    * Added -v and -vv options for INFO and DEBUG log levels respectively.

## v0.6.0

2017-09-22 Hologram <support@hologram.io>
    * Added program install verification steps to install script.

2017-09-20 Hologram <support@hologram.io>
    * Added hologram activate CLI subcommand. This allows developers to
      activate their SIM via the CLI instead of doing it on the dashboard.

2017-09-18 Hologram <support@hologram.io>
    * Added autodetection of USB modems and serial ports associated with those
      modems
    * Fix issue where scripts might hang when trying to use a serial port with
      ppp attached
    * Remove some redundant checks and unneeded initializations that were slowing
      things down

## v0.5.28

2017-09-12 Hologram <support@hologram.io>
    * Deprecated enable_inbound flag in HologramCloud constructor.
    * Suppress stack traces when user sends a SIGTERM while it's establishing
      a connection.

## v0.5.26

2017-09-01 Hologram <support@hologram.io>
    * Fixed topic parsing in hologram_send that can cause message body to be
      empty.

## v0.5.25

2017-08-31 Hologram <support@hologram.io>
    * Updated install script to include libpython2.7-dev as a require dependency.
    * added better error messages for unsupported operating systems/platforms.

## v0.5.23

2017-08-08 Hologram <support@hologram.io>
    * Fixed SMS timestamp issue. (wrong offset value)

2017-07-28 Hologram <support@hologram.io>
    * Added cellular modem id property in ISerial interface

2017-07-27 Hologram <support@hologram.io>
    * Fixed existing PPP session check whenever a double cellular connect is called.

2017-07-26 Hologram <support@hologram.io>
    * Made write interface public and added Serial unit tests.

2017-07-17 Hologram <support@hologram.io>
    * Refactored Serial interfaces.
    * Fixed bug where AT commands made might cause the serial buffer to be in
      an unexpected state that hang the modem.

2017-07-10 Hologram <support@hologram.io>
    * Renamed iota to Nova
    * Moved examples folder to the top level directory
    * Fixed false negative debug output that says a message isn't sent via OTP.

2017-06-20 Hologram <support@hologram.io>
    * Fixed incorrect pid parser that cause PPP processes to not be detected
      or killed.

2017-06-16 Hologram <support@hologram.io>
    * Fixed out of range Exception bug in modem location property.
    * Fixed bug in Location date property parser.

2017-06-06 Hologram <support@hologram.io>
    * Fixed regression on custom exceptions not having a handler.

2017-06-05 Hologram <support@hologram.io>
    * Updated requirements.txt to always use the latest python sdk auth package.
    * Added custom Hologram exceptions to the SDK.

2017-06-02 Hologram <support@hologram.io>
    * Fixed Hologram Spacebridge and Heartbeat

2017-06-01 Hologram <support@hologram.io>
    * Added better spacing for CLI help subcommand descriptions
    * Added default send cloud and receive data for Hologram CLI
    * Turned off exception stack trace when program is terminated via SIGTERM.
    * Better CLI messages and error handling (on CLI parameters + options).

2017-05-17 Hologram <support@hologram.io>
    * Added receive sms feature
    * Added auto PPP session detection
    * Threaded serial output buffer in the Serial interface to listen for URC events
    * Deprecated hologram_* CLI commands in favor of hologram <subcommand>s.
    * Added operator, location and modem type (name) properties for cellular modems.

2017-04-18 Hologram <support@hologram.io>
    * Deprecated cloud_id and cloud_key credentials in favor of a single devicekey.
    * Deprecated getSDKVersion() in favor of .version property.
    * Deprecated getNetworkType() in favor of .network_type property.
    * Deprecated mode choices in the modem interface.
    * Added sendPeriodicMessage() feature in CustomCloud + HologramCloud interface.
    * Added serial mode interface for cellular modems.
    * Deprecated chatScriptFile in favor of chatscript_file. Sticking to underscores
      for properties, camelCase for public methods/interfaces.
    * Added credentials property in authentication class.
    * Made certain properties persistent within the SDK (to minimize user errors
      when trying to set/change them after instantiation.

2017-04-03 Hologram <support@hologram.io>
    * Deprecated consumeReceivedMessage() interface in favor of popReceivedMessage()
    * Added more CLI scripts for sending messages via an active cellular connection.
    * Added CLI scripts that are automatically added to your PATH via setup.py.
    * Renamed default chatscript and moved it to a chatscripts folder under the modem interface

2017-03-16 Hologram <support@hologram.io>
    * Released hologram-python version 0.3.0
    * Added network interfaces for the Hologram SDK.
    * Added cellular network support via PPP for the iota, Huawei MS2131, and E303 modems.

2017-02-14 Hologram <support@hologram.io>
    * Released hologram-python version 0.2.0
    * Refactored Cloud interfaces - They are now named Cloud, CustomCloud and
      HologramCloud instead of Raw and Cloud.
    * Added more *Cloud interface unit tests
    * Added inbound connection interface.
    * Added socket timeout flags for both inbound and outbound interfaces.
    * Added and optimized Hologram CLI scripts.
    * HologramCloud now parses Hologram specific return types and alerts the
      user via the logging framework.

2017-02-01 Hologram <support@hologram.io>
    * Released hologram-python version 0.1.1
    * Added sendMessage and sendSMS functionality.
    * Examples and unit tests.
