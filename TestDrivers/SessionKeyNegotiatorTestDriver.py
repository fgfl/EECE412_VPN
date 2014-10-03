from SessionKeyNegotiator import *

testNeg1 = SessionKeyNegotiator()

testNeg2 = SessionKeyNegotiator()

while 1:
    test1 = testNeg1.get_public_key()
    print "Public Key 1"
    print test1

    test2 = testNeg2.get_public_key()
    print "Public Key 2"
    print test2

    key1 = testNeg1.get_session_key(test2)
    key2 = testNeg2.get_session_key(test1)

    print "Session Keys (Should be same)"
    print key1
    print key2
    print key2.bit_length()