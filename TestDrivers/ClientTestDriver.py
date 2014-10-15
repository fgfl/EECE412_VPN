from SecureVpn import *
import threading
from SessionKeyNegotiator import *

encrypter = SecureVpnCrypter()
negotiator = SessionKeyNegotiator("CLIENT")

client = SecureSvnClient(encrypter, negotiator, '192.168.0.2', 12345)
client.set_shared_secret("asdfasdfasdfasdfasdfasdf")
loop_thread = threading.Thread(target=asyncore.loop, name="Asyncore Loop", )
loop_thread.start()

while 1:
    message = raw_input("")
    client.send_message(message)