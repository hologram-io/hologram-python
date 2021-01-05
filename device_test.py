import os
from Hologram.HologramCloud import HologramCloud, ERR_OK

hologram = HologramCloud(dict(), network='cellular')

# Test basic serial communications
message = f"{message += hologram.network.modem_id} {hologram.network.signal_strength} {hologram.network.imsi} {hologram.network.iccid} {hologram.network.operator} {hologram.network.active_modem_interface}"

# Test Socket Sends
recv = hologram.sendMessage(message, topics=['TOPIC1', 'TOPIC2'], timeout=3)

if recv != ERR_OK:
    # Alert

credentials = {'devicekey': os.environ.get('DEVICE_KEY')}

hologram = HologramCloud(credentials, network='cellular', authentication_type='csrpsk')

# Test SMS
recv = hologram.sendSMS(os.environ.get('DEST_NUMBER'), 'Hi, SMS!')

if recv != ERR_OK:
    # Alert

# Test PPP
hologram = HologramCloud(dict(), authentication_type='sim-otp',
                             network='cellular')

hologram.network.scope = NetworkScope.HOLOGRAM  # Default route NOT set to cellular
result = hologram.network.connect()
if result == False:
     #Failed to connect to cell network

recv = hologram.sendMessage(message,
                            topics = ["TOPIC1","TOPIC2"],
                            timeout = 5)

if recv != ERR_OK:
    # Alert

hologram.network.disconnect()