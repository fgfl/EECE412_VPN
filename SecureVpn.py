import socket
import asyncore
import asynchat
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import threading


class MessageManager(object):

    NEGOTIATION_MESSAGE = "N"
    DATA_MESSAGE = "D"
    MESSAGE_DELIMITER = ";;"

    @staticmethod
    def parse_message(message):
        split_message = message.split(MessageManager.MESSAGE_DELIMITER)
        message_length = len(split_message)
        parsed_list = []
        i = 0
        while i < message_length - 1:
            parsed_list.append((split_message[i], split_message[i+1]))
            i += 2
        return parsed_list

    @staticmethod
    def create_message(message):
        message.replace(MessageManager.MESSAGE_DELIMITER, "")
        return MessageManager.DATA_MESSAGE + MessageManager.MESSAGE_DELIMITER + message + MessageManager.MESSAGE_DELIMITER

    @staticmethod
    def create_negotiation_message(public_key):
        return MessageManager.NEGOTIATION_MESSAGE + MessageManager.MESSAGE_DELIMITER + public_key + MessageManager.MESSAGE_DELIMITER


class SecureVpnCrypter(object):

    def __init__(self):
        self.randomBlockSize = Random.new().read(AES.block_size)
        self.crypter = None
        self.hasher = SHA256.new()

    def set_shared_secret(self, shared_secret):
        self.hasher.update(str(shared_secret))
        self.crypter = AES.new(self.hasher.digest(), AES.MODE_CFB, self.randomBlockSize)

    def encrypt(self, message):
        if self.crypter is None:
            raise Exception("Can not encrypt message, the encrypter has not been initialized yet!")
        return self.crypter.encrypt(self.randomBlockSize + message)

    def decrypt(self, cipher_text):
        if self.crypter is None:
            raise Exception("Can not decrypt message, the encrypter has not been initialized yet!")
        decrypted_message = self.crypter.decrypt(cipher_text)[16:]
        return decrypted_message


class SecureSvnBase(asynchat.async_chat):

    def __init__(self, crypter, negotiator):
        asynchat.async_chat.__init__(self)
        self.received_data = ''
        self.crypter = crypter
        self.negotiator = negotiator
        self.set_terminator(MessageManager.MESSAGE_DELIMITER)

    def collect_incoming_data(self, data):
        self.received_data += data

    def found_terminator(self):
        self.process_message()

    def send_negotiation(self, public_key):
        self.send(self.crypter.encrypt(MessageManager.create_negotiation_message(str(public_key))) + MessageManager.MESSAGE_DELIMITER)

    def send_message(self, message):
        self.send(self.crypter.encrypt(MessageManager.create_message(message)) + MessageManager.MESSAGE_DELIMITER)

    def set_shared_secret(self, shared_secret):
        self.crypter.set_shared_secret(shared_secret)


class SecureSvnClient(SecureSvnBase):

    def __init__(self, crypter, negotiator, host, port):
        SecureSvnBase.__init__(self, crypter, negotiator)
        self.host = host
        self.port = port
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))

    def process_message(self):

        encrypted_text = self.received_data
        decrypted_text = self.crypter.decrypt(encrypted_text)

        messages = MessageManager.parse_message(decrypted_text)

        for message in messages:
            message_type, content = message

            if message_type == MessageManager.DATA_MESSAGE:
                print "The received plain text is: " + content

            elif message_type == MessageManager.NEGOTIATION_MESSAGE:
                new_public_key = self.negotiator.get_public_key()
                self.send_negotiation(new_public_key)
                print "Sending Negotiation With Key:"
                print new_public_key
                print "Received Public Key: " + content
                new_session_key = self.negotiator.get_session_key(content)
                self.crypter.set_shared_secret(new_session_key)
                print "Received Negotiation. New Session Key Is:"
                print new_session_key
        self.received_data = ''


class SecureSvnServerHandler(SecureSvnBase):

    renegotiation_time = 5

    def __init__(self, crypter, negotiator, sock):
        SecureSvnBase.__init__(self, crypter, negotiator)
        self.set_socket(sock)
        self.initiate_key_negotiation()

    def process_message(self):
        encrypted_text = self.received_data
        decrypted_text = self.crypter.decrypt(encrypted_text)

        messages = MessageManager.parse_message(decrypted_text)

        for message in messages:
            message_type, content = message

            if message_type == MessageManager.DATA_MESSAGE:
                print "The received plain text is: " + content

            elif message_type == MessageManager.NEGOTIATION_MESSAGE:
                print "Received Public Key: " + content
                new_session_key = self.negotiator.get_session_key(content)
                self.crypter.set_shared_secret(new_session_key)
                print "Received Negotiation. New Session Key Is:"
                print new_session_key
        self.received_data = ''

    def initiate_key_negotiation(self):
        new_public_key = self.negotiator.get_public_key()
        self.send_negotiation(new_public_key)
        print "Sending Negotiation With Key:"
        print new_public_key
        threading.Timer(SecureSvnServerHandler.renegotiation_time, self.initiate_key_negotiation).start()


class SecureSvnServer(asyncore.dispatcher):

    def __init__(self, host, port, crypter, negotiator):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.crypter = crypter
        self.host = host
        self.port = port
        self.negotiator = negotiator
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.handler = None

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, address = pair
            print 'Incoming connection from %s' % repr(address)
            self.handler = SecureSvnServerHandler(self.crypter, self.negotiator, sock)

    def send_message(self, message):
        if self.handler is not None:
            self.handler.send_message(message)

    def set_shared_secret(self, shared_secret):
        self.crypter.set_shared_secret(shared_secret)