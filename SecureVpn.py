import socket
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


class SecureVpnServer(object):

        def __init__(self, crypter):
            self.crypter = crypter
            self.host = ""
            self.port = 0
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        def set_host(self, host):
            self.host = host

        def set_port(self, server_port):
            self.port = server_port

        def set_shared_secret(self, shared_secret):
            self.crypter.set_shared_secret(shared_secret)

        def start_server(self):
            try:
                self.socket.bind((self.host, self.port))
            except socket.error as error_message:
                print 'Bind failed. Error Code: ' + str(error_message[0]) + ' Message ' + error_message[1]
            print 'Socket bind complete'
            self.socket.listen(10)
            print 'Socket now listening'

        def wait_for_connection(self):
            while 1:
                try:
                    connection, address = self.socket.accept()
                    print 'Connected with ' + address[0] + ':' + str(address[1])
                    connection.send("Welcome to the Secure Python VPN!")
                    while 1:
                        received_cipher_text = connection.recv(512)
                        print "We received this cipher text: " + received_cipher_text
                        print "The plain text is: " + self.crypter.decrypt(received_cipher_text)
                    connection.close()
                except socket.error as error_message:
                    print 'There has been an error with the connection: ' + str(error_message[0]) + ' Message ' + error_message[1]

        def close_server(self):
                self.socket.close()


class SecureVpnClient(object):

        def __init__(self, crypter):
            self.crypter = crypter
            self.host = ""
            self.port = 0
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        def set_host(self, host):
            self.host = host

        def set_port(self, server_port):
            self.port = server_port

        def set_shared_secret(self, shared_secret):
            self.crypter.set_shared_secret(shared_secret)

        def connect_to_server(self):
            try:
                self.socket.connect((self.host, self.port))
                return 0
            except socket.error as error_message:
                print 'Connection failed. Error Code : ' + str(error_message[0]) + ' Message ' + error_message[1]
                return 1

        def send_message(self, message):
            encrypted_message = self.crypter.encrypt(message)
            self.socket.send(encrypted_message)

        def close_client(self):
            self.socket.close()