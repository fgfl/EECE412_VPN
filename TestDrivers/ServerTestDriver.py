from SecureVpn import *
import threading
from SessionKeyNegotiator import *

encrypter = SecureVpnCrypter()
negotiator = SessionKeyNegotiator("SERVER")

server = SecureSvnServer('localhost', 12345, encrypter, negotiator)
server.set_shared_secret("asdfasdfasdfasdfasdfasdf")

loop_thread = threading.Thread(target= asyncore.loop, name="Asyncore Loop")
loop_thread.start()

while 1:
    message = raw_input("")
    server.send_message(message)