from SecureVpn import *

encrypter = SecureVpnEncrypter()

testServer = SecureVpnServer(encrypter)
testServer.set_host("localhost")
testServer.set_port(12345)
testServer.set_shared_secret("ThisTHISTestTEST")

testServer.start_server()
testServer.wait_for_connection()
testServer.close_socket()