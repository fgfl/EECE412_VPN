from SecureVpn import *
import threading
from SessionKeyNegotiator import *
from SecureVpnCrypter import *

encrypter = SecureVpnCrypter()
negotiator = SessionKeyNegotiator("SERVER")

server = SecureVpnServer('', 12345, encrypter, negotiator)
server.set_shared_secret("asdfasdfasdfasdfasdfasdf")

loop_thread = threading.Thread(target=asyncore.loop, name="Asyncore Loop")
loop_thread.start()

while 1:
    message = raw_input("")
    server.send_message(message)