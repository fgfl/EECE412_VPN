from SecureVpn import *

encrypter = SecureVpnCrypter()

testClient = SecureVpnClient(encrypter)
testClient.set_host("localhost")
testClient.set_port(12345)
testClient.set_shared_secret("ThisTHISTestTEST")

if testClient.connect_to_server() == 0:
    while 1:
        message = raw_input('Enter message to send: ')
        testClient.send_message(message)