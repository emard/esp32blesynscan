# This example as wifi client
# should connects to remote synscan wifi access point
# actually it doesn't connect, something's not working

# FIXME no reply

from os import dupterm
from machine import Pin, Timer
from time import sleep
import network
import socket

ledpin = Pin(21, mode=Pin.OUT)
NAME="SynScan_1234"
PASS=""
DEBUG=1
ip_address = "192.168.4.2"
subnet = "255.255.255.0"
gateway = "192.168.4.1"
dns = "192.168.4.1"

wifi_connected = False

def init_wifi_client():
  global wifi, udp_socket, ble_tx, ble_rx, led_timer
  sleep(1)
  print("starting client")
  wifi = network.WLAN(network.STA_IF)
  wifi.active(False)
  wifi.active(True)
  print("connecting to", NAME, PASS)
  wifi.connect(NAME, PASS)
  while wifi.active() == False:
    pass
  # wifi.ifconfig((ip_address, subnet, gateway, dns))
  udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  udp_socket.bind(('', 11880))
  _SO_REGISTER_HANDLER = const(20)
  udp_socket.setsockopt(socket.SOL_SOCKET, _SO_REGISTER_HANDLER, udp_recv)
  led_timer=Timer(0)
  led_timer.init(mode=Timer.PERIODIC, period=1000, callback=led_wifi)

def led_wifi(dummy):
 global wifi_connected
 if wifi.isconnected()==True:
   led(1)
   if(wifi_connected==False):
     if DEBUG:
       print(wifi.ifconfig())
   wifi_connected=True
 else:
   led(0)
   wifi_connected=False

def udp_recv(udp):
  led(0)
  request, source = udp.recvfrom(256)
  if len(request):
    print(request)
    # response = wire_txrx(request)
    response = request
    #if len(response):
    #  udp.sendto(response, source)
  led(1)

def udp_send(data):
  dest = ("192.168.4.1", 11880)
  print(data,dest)
  udp_socket.sendto(data, dest)

def led(val):
  ledpin.value(val^1)

def run():
  init_wifi_client()

run()
# sending ":e1\r"
print("wifiremote.udp_send(b\":e1\\r\")")
# should reply with b'=0324AF\r'
