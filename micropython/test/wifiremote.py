# This example as wifi client
# connects to remote synscan wifi access point

# ESP32S3 SPIRAM FIXME
# connection to PC AP is unreliable, significant ping packet loss
# no connection to SynScan

# ESP32C3 WORKS
# connection to SynScan OK
# >>> wifiremote.udp_send(b":e1\r")
# b':e1\r' ('192.168.4.1', 11880)
# >>> b'=0328AF\r'

from machine import Pin, Timer
import network
import socket

#ledpin = Pin(2, mode=Pin.OUT) # esp32
ledpin = Pin(21, mode=Pin.OUT) # esp32s3
NAME="SynScan_1234" # connect to this AP name
PASS="" # this password

wifi_connected = False
gateway = "0.0.0.0"
port = const(11880) # default synscan udp port

def init_wifi_client():
  global wifi, udp_socket, ble_tx, ble_rx, led_timer
  print("starting client")
  wifi = network.WLAN(network.STA_IF)
  wifi.active(False)
  while wifi.active() == True:
    pass
  wifi.active(True)
  while wifi.active() == False:
    pass
  print("connecting to", NAME, PASS)
  wifi.connect(NAME, PASS)
  udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  udp_socket.bind(('', port))
  _SO_REGISTER_HANDLER = const(20)
  udp_socket.setsockopt(socket.SOL_SOCKET, _SO_REGISTER_HANDLER, udp_recv)
  led_timer=Timer(0)
  led_timer.init(mode=Timer.PERIODIC, period=1000, callback=led_wifi)

def led_wifi(dummy):
 global wifi_connected, gateway
 if wifi.isconnected()==True:
   led(1)
   if(wifi_connected==False):
     print(wifi.ifconfig()) 
     # ("    IP     ", "   NETMASK   ", "  GATEWAY  ", "    DNS    ")
     # ("192.168.4.2", "255.255.255.0", "192.168.4.1", "192.168.4.1")
   wifi_connected=True
   gateway = wifi.ifconfig()[2] # udp_send() to gateway IP
   # gateway = "192.168.4.1" # always the same, never changes
   udp_send(b":e1\r")
   # response should be something like b'=0324AF\r'
 else:
   led(0)
   wifi_connected=False

def udp_recv(udp):
  global gateway
  led(0)
  response, source = udp.recvfrom(256)
  if len(response):
    print(response)
  led(1)

def udp_send(data):
  dest = (gateway, port)
  print(data,dest)
  udp_socket.sendto(data, dest)

def led(val):
  ledpin.value(val^1)

def run():
  init_wifi_client()

run()
