import socket
import asyncore
import asynchat
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import threading
import mutex
import datetime


class MessageManager(object):

    CHALLENGE = "C"
    NEGOTIATION_MESSAGE = "N"
    NEGOTIATION_CHALLENGE = "NCH"
    NEGOTIATION_CONFIRMATION_MESSAGE = "NC"
    NEGOTIATION_INITIALIZATION_MESSAGE = "NI"
    DATA_MESSAGE = "D"
    MESSAGE_DELIMITER = "------------"
    MULTI_MESSAGE_DELIMITER = "!!!!!!!!!!!!!!!!"

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
    def create_negotiation_confirmation_message():
        return MessageManager.NEGOTIATION_CONFIRMATION_MESSAGE + MessageManager.MESSAGE_DELIMITER + MessageManager.MESSAGE_DELIMITER

    @staticmethod
    def create_negotiation_initialization_message():
        return MessageManager.NEGOTIATION_INITIALIZATION_MESSAGE + MessageManager.MESSAGE_DELIMITER + MessageManager.MESSAGE_DELIMITER

    @staticmethod
    def create_challenge_message(negotiator):
         return MessageManager.CHALLENGE + MessageManager.MESSAGE_DELIMITER + negotiator.get_challenge() + MessageManager.MESSAGE_DELIMITER

    @staticmethod
    def create_challenge_response_message(negotiator, shared_secret):
        newChallenge, response = negotiator.get_challenge_response(shared_secret)
        responseMessage = MessageManager.NEGOTIATION_CHALLENGE + MessageManager.MESSAGE_DELIMITER + str(response) + MessageManager.MESSAGE_DELIMITER
        challengeMessage = MessageManager.CHALLENGE + MessageManager.MESSAGE_DELIMITER + str(newChallenge) + MessageManager.MESSAGE_DELIMITER
        return challengeMessage, responseMessage

    @staticmethod
    def create_challenge_negotiation_message(negotiator, shared_secret):
        return MessageManager.NEGOTIATION_MESSAGE + MessageManager.MESSAGE_DELIMITER + negotiator.get_challenge_negotiation(shared_secret) + MessageManager.MESSAGE_DELIMITER

class SecureVpnCrypter(object):

    encryptionTag = "EEEEEEEE"

    def __init__(self):
        self.crypter = None
        self.randomBlockSize = Random.new().read(AES.block_size)
        self.hasher = SHA256.new()

    def set_shared_secret(self, shared_secret):
        self.hasher.update(str(shared_secret))
        self.apply_new_iv()

    def apply_new_iv(self):
        self.randomBlockSize = Random.new().read(AES.block_size)
        self.crypter = AES.new(self.hasher.digest(), AES.MODE_CFB, self.randomBlockSize)

    def encrypt(self, message):
        if self.crypter is None:
            raise Exception("Can not encrypt message, the encrypter has not been initialized yet!")
        self.apply_new_iv()
        return SecureVpnCrypter.encryptionTag + str(self.crypter.encrypt(self.randomBlockSize + message))

    def decrypt(self, cipher_text):
        if self.crypter is None:
            raise Exception("Can not decrypt message, the encrypter has not been initialized yet!")

        decrypted_message = cipher_text

        if str(cipher_text[0:len(SecureVpnCrypter.encryptionTag)]) == SecureVpnCrypter.encryptionTag:
            trimmed_message = cipher_text[len(SecureVpnCrypter.encryptionTag):]
            decrypted_message = self.crypter.decrypt(trimmed_message)[16:]

        return decrypted_message


class SecureSvnBase(asynchat.async_chat):

    def __init__(self, crypter, negotiator):
        asynchat.async_chat.__init__(self)
        self.received_data = ''
        self.crypter = crypter
        self.negotiator = negotiator
        self.set_terminator(MessageManager.MULTI_MESSAGE_DELIMITER)
        self.negotiation_lock = mutex.mutex()
        self.progress_lock = mutex.mutex()
        self.in_step_through_mode = False
        self.shared_secret = ""

        self.logger = None
        self.debugger = None

    def set_logger(self, logger):
        self.logger = logger

    def set_debugger(self, debugger):
        self.debugger = debugger

    def log(self, message):
        if self.logger is not None:
            self.logger(message)

    def debug(self, message):
        if self.debugger is not None:
            self.debugger(message)

    def collect_incoming_data(self, data):
        self.received_data += data

    def found_terminator(self):
        self.process_message()

    def append_message_delimiters(self, message):
        return message + MessageManager.MULTI_MESSAGE_DELIMITER

    def send_challenge(self):
        self.wait_and_begin_progress()
        self.send(self.append_message_delimiters(MessageManager.create_challenge_message(self.negotiator)))

    def send_challenge_response(self):
        self.wait_and_begin_progress()
        challengeMessage, responseMessage = MessageManager.create_challenge_response_message(self.negotiator, self.shared_secret)
        self.send(self.append_message_delimiters(challengeMessage))
        self.send(self.append_message_delimiters(self.crypter.encrypt(responseMessage)))

    def send_challenge_negotiation(self):
        self.wait_and_begin_progress()
        self.send(self.append_message_delimiters(self.crypter.encrypt(MessageManager.create_challenge_negotiation_message(self.negotiator, self.shared_secret))))

    def confirm_negotiation(self):
        self.wait_and_begin_progress()
        self.send(self.append_message_delimiters(self.crypter.encrypt(MessageManager.create_negotiation_confirmation_message())))

    def initialize_negotiation(self):
        self.wait_and_begin_progress()
        self.send(self.append_message_delimiters(self.crypter.encrypt(MessageManager.create_negotiation_initialization_message())))

    def send_message(self, message):
        self.wait_and_begin_progress()
        self.wait_for_negotiation()
        self.send(self.append_message_delimiters(self.crypter.encrypt(MessageManager.create_message(message))))

    def set_shared_secret(self, shared_secret):
        self.shared_secret = shared_secret
        self.crypter.set_shared_secret(shared_secret)

    def wait_and_begin_progress(self):
        if self.in_step_through_mode:
            while not self.progress_lock.testandset():
                None

    def continue_progress(self):
        self.progress_lock.unlock()

    def wait_and_begin_negotiation(self):
        while not self.negotiation_lock.testandset():
            None

    def wait_for_negotiation(self):
        while self.negotiation_lock.locked:
            None

    def toggle_step_through_mode(self):
        self.in_step_through_mode = not self.in_step_through_mode

class SecureSvnClient(SecureSvnBase):

    def __init__(self, crypter, negotiator, host, port):
        SecureSvnBase.__init__(self, crypter, negotiator)
        self.host = host
        self.port = port
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))

    def process_message(self):

        encrypted_text = self.received_data
        self.debug(encrypted_text)
        decrypted_text = self.crypter.decrypt(encrypted_text)

        messages = MessageManager.parse_message(decrypted_text)

        for message in messages:
            message_type, content = message

            if message_type == MessageManager.DATA_MESSAGE:
                self.log("The received plain text is: " + content)
                print "The received plain text is: " + content

            elif message_type == MessageManager.CHALLENGE:
                self.negotiator.record_challenge(content)

            elif message_type == MessageManager.NEGOTIATION_CHALLENGE:
                print "Negotiation is: " + str(content)
                self.log("Negotiation is: " + str(content))
                if self.negotiator.validate_response(content, self.shared_secret):
                    self.send_challenge_negotiation()
                    self.set_shared_secret(self.negotiator.get_session_key(content))
                else:
                    self.log("INVALID - DISCONNECTING")
                    print "INVALID - DISCONNECTING"
                    self.socket.close()

            elif message_type == MessageManager.NEGOTIATION_CONFIRMATION_MESSAGE:
                self.handle_negotiation_confirmation()

            elif message_type == MessageManager.NEGOTIATION_INITIALIZATION_MESSAGE:
                while not self.negotiation_lock.testandset():
                    None
                self.send_challenge()

        self.received_data = ''

    def handle_negotiation_confirmation(self):
        self.negotiation_lock.unlock()


class SecureSvnServerHandler(SecureSvnBase):

    renegotiation_time = 20

    def __init__(self, crypter, negotiator, sock, shared_secret):
        SecureSvnBase.__init__(self, crypter, negotiator)
        self.set_socket(sock)
        self.shared_secret = shared_secret
        self.initiate_key_negotiation()

    def process_message(self):

        encrypted_text = self.received_data
        self.debug(encrypted_text)

        decrypted_text = self.crypter.decrypt(encrypted_text)

        messages = MessageManager.parse_message(decrypted_text)

        for message in messages:
            message_type, content = message

            if message_type == MessageManager.DATA_MESSAGE:
                self.log("The received plain text is: " + content)
                print "The received plain text is: " + content

            elif message_type == MessageManager.CHALLENGE:
                self.log("Challenge is: " + str(content))
                print "Challenge is: " + str(content)
                self.negotiator.record_challenge(content)
                self.send_challenge_response()

            elif message_type == MessageManager.NEGOTIATION_MESSAGE:
                self.log("Negotiation is: " + str(content))
                print "Negotiation is: " + str(content)
                if self.negotiator.validate_response(content, self.shared_secret):
                    self.set_shared_secret(self.negotiator.get_session_key(content))
                    self.confirm_negotiation()
                    self.negotiation_lock.unlock()
                else:
                    self.log("INVALID - DISCONNECTING")
                    print "INVALID - DISCONNECTING"
                    self.socket.close()

        self.received_data = ''

    def initiate_key_negotiation(self):
        self.wait_for_negotiation()
        print "Initializing negotiation..."
        self.initialize_negotiation()
        self.wait_and_begin_negotiation()
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
        self.shared_secret = ""
        self.logger = None
        self.debugger = None

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, address = pair
            print 'Incoming connection from %s' % repr(address)
            self.handler = SecureSvnServerHandler(self.crypter, self.negotiator, sock, self.shared_secret)
            self.handler.set_logger(self.logger)
            self.handler.set_debugger(self.debugger)

    def send_message(self, message):
        if self.handler is not None:
            self.handler.send_message(message)

    def set_shared_secret(self, shared_secret):
        self.shared_secret = shared_secret
        self.crypter.set_shared_secret(shared_secret)

    def continue_progress(self):
        self.handler.continue_progress()

    def set_logger(self, logger):
        self.logger = logger

    def set_debugger(self, debugger):
        self.debugger = debugger