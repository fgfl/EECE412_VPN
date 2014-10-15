from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random


class SecureVpnCrypter(object):

    def __init__(self):
        self.crypter = None
        self.iv = Random.new().read(AES.block_size)
        self.secret_hasher = SHA256.new()
        self.integrity_hasher_decrypt = SHA256.new()
        self.integrity_hasher_encrypt = SHA256.new()

    def set_shared_secret(self, shared_secret):
        self.secret_hasher = SHA256.new(str(shared_secret))
        self.apply_new_iv()

    def apply_new_iv(self):
        self.iv = Random.new().read(AES.block_size)
        self.crypter = AES.new(self.secret_hasher.digest(), AES.MODE_CFB, self.iv)

    def encrypt(self, message):
        if self.crypter is None:
            raise Exception("Can not encrypt message, the encrypter has not been initialized yet!")
        self.apply_new_iv()

        encrypted_message = str(self.crypter.encrypt(message))

        self.integrity_hasher_encrypt = SHA256.new(str(message))
        integrity_hash = self.integrity_hasher_encrypt.digest()

        return integrity_hash, self.iv + encrypted_message

    def decrypt(self, cipher_text, integrity_hash):
        if self.crypter is None:
            raise Exception("Can not decrypt message, the encrypter has not been initialized yet!")

        decrypted_message = self.crypter.decrypt(cipher_text)[16:]

        self.integrity_hasher_decrypt = SHA256.new(str(decrypted_message))
        message_hash = self.integrity_hasher_decrypt.digest()

        if integrity_hash is not None:
            if str(message_hash) != str(integrity_hash):
                return False, decrypted_message


        return True, decrypted_message
