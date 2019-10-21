# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.7.4 (default, Sep  7 2019, 18:27:02) 
# [Clang 10.0.1 (clang-1001.0.46.4)]
# Embedded file name: build/bdist.linux-armv7l/egg/HologramAuth/Holohash.py
# Compiled at: 2019-08-27 17:24:30
import binascii
from Crypto.Hash import HMAC
from Crypto.Hash import SHA256

__XOR__ = lambda x, y: chr(ord(x) ^ ord(y))

class Holohash(object):

    def __init__(self):
        pass

    def __parse_sim_milenage_at_response(self, resp):
        resp = resp[:-6]
        sres_length = int(resp[:2]) * 2
        sres = binascii.unhexlify(resp[2:sres_length + 2])
        resp = resp[sres_length + 2:]
        kc_length = int(resp[:2]) * 2
        kcstr = resp[2:kc_length + 2]
        kc = binascii.unhexlify(kcstr)
        kc = kc[:-1] + chr(ord(kc[(-1)]) & 252)
        return (
         sres, kc)

    def generate_milenage_token(self, response, device_time):
        sres, kc = self.__parse_sim_milenage_at_response(response)
        hmac_key2 = ((sres + kc) * 3)[:32]
        return self.__hmac_sha256(key=hmac_key2, msg=device_time)

    def generate_sim_gsm_milenage_command(self, imsi, iccid, nonce, device_time):
        nonce = binascii.unhexlify(nonce)
        hmac_key = self.__logical_xor((imsi + iccid) * 6, nonce)
        rand_parts = binascii.unhexlify(self.__hmac_sha256(key=hmac_key, msg=device_time))
        rand_part_1 = rand_parts[:len(rand_parts) / 2]
        rand_part_2 = rand_parts[len(rand_parts) / 2:]
        rand = self.__logical_xor(rand_part_1, rand_part_2)
        return str(binascii.hexlify(rand)).upper()

    def __logical_xor(self, str1, str2):
        return ('').join(__XOR__(x, y) for x, y in zip(str1, str2))

    def __hmac_sha256(self, key, msg):
        hasher = HMAC.new(key=key, msg=msg, digestmod=SHA256)
        return hasher.hexdigest()