from SecureVpn import *
import threading

encrypter = SecureVpnCrypter()

server = SecureSvnServer('localhost', 12345, encrypter)
server.set_shared_secret("TestTESTPassPASS")

loop_thread = threading.Thread(target=asyncore.loop, name="Asyncore Loop")
loop_thread.start()

while 1:
    message = raw_input("")
    server.send_message(message)