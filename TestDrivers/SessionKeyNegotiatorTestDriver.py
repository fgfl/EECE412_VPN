from SessionKeyNegotiator import *

testNeg1 = SessionKeyNegotiator()

testNeg2 = SessionKeyNegotiator()

test1 = testNeg1.get_negotiation_message()
print "Negotiation 1"
print test1

test2 = testNeg2.get_negotiation_message()
print "Negotiation 2"
print test2

key1 = testNeg1.get_session_key(test2)
key2 = testNeg2.get_session_key(test1)

print "Keys (Should be same)"
print key1
print key2