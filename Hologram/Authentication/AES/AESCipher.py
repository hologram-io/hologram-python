from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class AESCipher(object):

    # EFFECTS: Constructor that sets the IV to
    def __init__(self, iv, key):
        self.iv = iv
        backend = default_backend()
        self.cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        self.encryptor = self.cipher.encryptor()
        self.decryptor = self.cipher.decryptor()

    # EFFECTS: Encrypts the given plaintext in AES CBC mode. returns a cipher text.
    def AES_cbc_encrypt(self, plaintext):
        plaintext = self.padPKCS7(plaintext)
        ciphertext = self.encryptor.update(plaintext)
        return ciphertext

    # EFFECTS: Encrypts the given ciphertext in AES CBC mode. returns a plaintext.
    def AES_cbc_decrypt(self, ciphertext):
        plaintext = self.decryptor.update(ciphertext)
        return plaintext

    # EFFECTS: Pads the PKCS7
    def padPKCS7(self, newPlainText):
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(newPlainText)
        padded_data += padder.finalize()
        return padded_data
