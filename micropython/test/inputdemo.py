# demo how to use standard pytion "input" command
# to read input data terminated by "\r"
# convert to bytearray send over udp
# to get response in bytearray form
# print response which should be only
# "\r" terminated, not "\r\n"

# ctrl-c exits to micropython prompt

def run():
  for i in range(10):
    request=input("").encode("utf-8")+b"\r"
    response=b"="+request
    print(request,response)
    print(response.decode("utf-8"),end="")
    print("")
run()
