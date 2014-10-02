import socket
import asyncore
from Crypto.Cipher import AES
from Crypto import Random


class SecureVpnCrypter(object):

    def __init__(self):
        self.randomBlockSize = Random.new().read(AES.block_size)
        self.crypter = None

    def set_shared_secret(self, shared_secret):
        self.crypter = AES.new(shared_secret, AES.MODE_CFB, self.randomBlockSize)

    def encrypt(self, message):
        if self.crypter is None:
            raise Exception("Can not encrypt message, the encrypter has not been initialized yet!")
        return self.crypter.encrypt(self.randomBlockSize + message)

    def decrypt(self, cipher_text):
        if self.crypter is None:
            raise Exception("Can not decrypt message, the encrypter has not been initialized yet!")
        decrypted_message = self.crypter.decrypt(cipher_text)[16:]
        return decrypted_message


class SecureSvnBase(asyncore.dispatcher):

    def __init__(self, host, port, crypter):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer = ""
        self.crypter = crypter
        self.host = host
        self.port = port

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        encrypted_text = self.recv(8192)
        decrypted_text = self.crypter.decrypt(encrypted_text)
        print "The received encrypted text is: " + encrypted_text
        print "The received plain text is: " + decrypted_text

    def writable(self):
        return len(self.buffer) > 0

    def handle_write(self):
        buffer_to_send = self.crypter.encrypt(self.buffer)
        sent = len(buffer_to_send)
        self.send(buffer_to_send)
        self.buffer = self.buffer[sent:]

    def set_shared_secret(self, shared_secret):
        self.crypter.set_shared_secret(shared_secret)

    def send_message(self, message):
        self.buffer += message


class SecureSvnServer(SecureSvnBase):

    def __init__(self, host, port, crypter):
        SecureSvnBase.__init__(self, host, port, crypter)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.handler = None

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            socket, address = pair
            print 'Incoming connection from %s' % repr(address)
            self.handler = SecureSvnServerHandler(socket, self.crypter)

    def send_message(self, message):
        if self.handler is not None:
            self.handler.send_message(message)


class SecureSvnClient(SecureSvnBase):

    def __init__(self, host, port, crypter):
        SecureSvnBase.__init__(self, host, port, crypter)
        self.connect((host, port))


class SecureSvnServerHandler(asyncore.dispatcher_with_send):

    def __init__(self, socket, crypter):
        asyncore.dispatcher_with_send.__init__(self, socket)
        self.crypter = crypter
        self.buffer = ""

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        encrypted_text = self.recv(8192)
        decrypted_text = self.crypter.decrypt(encrypted_text)
        print "The received encrypted text is: " + encrypted_text
        print "The received plain text is: " + decrypted_text

    def writable(self):
        return len(self.buffer) > 0

    def handle_write(self):
        buffer_to_send = self.crypter.encrypt(self.buffer)
        sent = len(buffer_to_send)
        self.send(buffer_to_send)
        self.buffer = self.buffer[sent:]

    def send_message(self, message):
        self.buffer += message