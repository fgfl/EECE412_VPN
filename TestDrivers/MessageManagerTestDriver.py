from SecureVpn import *

test = MessageManager("")

return_list = test.parse_message("D;;This is a message!;;D;;This is another one!;;N;;123456789;;")

print return_list[0]