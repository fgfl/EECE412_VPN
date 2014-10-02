import random
import math

class SessionKeyNegotiator(object):

    g = 2
    p = 93420252879477171382948704041913678054313750920611664727979254281502122975686

    def __init__(self):
        self.a = long(0)
        random.seed()

    def set_self_key(self):
        self.a = random.getrandbits(13)

    def get_negotiation_message(self):
        self.set_self_key()
        return long((SessionKeyNegotiator.g ** self.a) % SessionKeyNegotiator.p)

    def get_session_key(self, negotiation_response):
        return long((negotiation_response ** self.a) % SessionKeyNegotiator.p)
