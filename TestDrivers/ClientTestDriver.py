from SecureVpn import *
import threading

encrypter = SecureVpnCrypter()

client = SecureSvnClient('localhost', 12345, encrypter)
client.set_shared_secret("TestTESTPassPASS")

loop_thread = threading.Thread(target=asyncore.loop, name="Asyncore Loop")
loop_thread.start()

while 1:
    message = raw_input("")
    client.send_message(message)