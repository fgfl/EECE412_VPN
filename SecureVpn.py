import socket
from Crypto.Cipher import AES
from Crypto import Random


class SecureVpnEncrypter(object):

    def __init__(self):
        self.randomBlockSize = Random.new().read(AES.block_size)
        self.encrypter = None

    def initialize_encrypter(self, shared_secret):
        self.encrypter = AES.new(shared_secret, AES.MODE_CFB, self.randomBlockSize)

    def encrypt(self, message):
        if self.encrypter is None:
            raise Exception("Can not encrypt message, the encrypter has not been initialized yet!")
        return self.encrypter.encrypt(message)

    def decrypt(self, cipher_text):
        if self.encrypter is None:
            raise Exception("Can not decrypt message, the encrypter has not been initialized yet!")
        return self.encrypter.decrypt(cipher_text)


class SecureVpnServer(object):

        def __init__(self, encrypter):
            self.encrypter = encrypter
            self.host = ""
            self.port = 0
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        def set_host(self, host):
            self.host = host

        def set_port(self, server_port):
            self.port = server_port

        def set_shared_secret(self, shared_secret):
            self.encrypter.initialize_encrypter(shared_secret)

        def start_server(self):
            try:
                self.socket.bind((self.host, self.port))
            except socket.error as error_message:
                print 'Bind failed. Error Code : ' + str(error_message[0]) + ' Message ' + error_message[1]
            print 'Socket bind complete'
            self.socket.listen(10)
            print 'Socket now listening'

        def wait_for_connection(self):
            while 1:
                connection, address = self.socket.accept()
                print 'Connected with ' + address[0] + ':' + str(address[1])
                connection.send("Welcome to the Secure Python VPN!")
                while 1:
                    received_cipher_text = connection.recv(512)
                    print "We received this cipher text: " + received_cipher_text
                    print "The plain text is: " + self.encrypter.decrypt(received_cipher_text)
                connection.close()

        def close_server(self):
                self.socket.close()


class SecureVpnClient(object):

        def __init__(self, encrypter):
            self.encrypter = encrypter
            self.host = ""
            self.port = 0
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        def set_host(self, host):
            self.host = host

        def set_port(self, server_port):
            self.port = server_port

        def set_shared_secret(self, shared_secret):
            self.encrypter.initialize_encrypter(shared_secret)

        def connect_to_server(self):
            try:
                self.socket.connect((self.host, self.port))
                return 0
            except socket.error as error_message:
                print 'Connection failed. Error Code : ' + str(error_message[0]) + ' Message ' + error_message[1]
                return 1

        def send_message(self, message):
            encrypted_message = self.encrypter.encrypt(message)
            self.socket.send(encrypted_message)

        def close_client(self):
            self.socket.close()