# mpremote run uartest.py

import os
from machine import UART
from time import sleep_ms

print("detaching prompt from ttl serial")
os.dupterm(None,0) # detach prompt from slot 1 UART pins 43,44)
print("prompt detached from ttl serial")
uart=UART(1,baudrate=9600,tx=43,rx=44,timeout=50,timeout_char=2)

while 1:
  print("send :e1")
  uart.write(":e1\r")
  print(uart.read()) # read echoed command
  sleep_ms(200)
