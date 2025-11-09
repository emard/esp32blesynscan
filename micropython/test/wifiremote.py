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

import os
from machine import Pin, Timer
from time import sleep
import network
import socket

ledpin = Pin(21, mode=Pin.OUT)
NAME="SynScan_1234"
PASS=""
DEBUG=1
ip_address = "192.168.48.171"
subnet = "255.255.255.0"
gateway = "192.168.48.254"
dns = "192.168.48.254"

wifi_connected = False

def init_wifi_client():
  global wifi, udp_socket, ble_tx, ble_rx, led_timer
  sleep(1)
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
  wifi.ifconfig()
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
print(os.uname())
print("wifiremote.udp_send(b\":e1\\r\")")
# should reply with b'=0324AF\r'
