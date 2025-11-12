# micropython >= 1.25

# from linux cmdline:
# mpremote run synscan.py

# from micropython cmdline:
# import synscan

from os import dupterm
from machine import Pin, UART, Timer
import synscan_cfg

NAME=synscan_cfg.NAME # BLE client name max 14 chars
PASS=synscan_cfg.PASS # Wifi password min 8 chars
PIN_LED=synscan_cfg.PIN_LED # board LED
UART_INIT=synscan_cfg.UART_INIT
AP_CHANNEL=synscan_cfg.AP_CHANNEL
WIRELESS=synscan_cfg.WIRELESS
BLE=synscan_cfg.BLE
REPLACE=synscan_cfg.REPLACE
DEBUG=synscan_cfg.DEBUG
LOG=synscan_cfg.LOG
MOTOR_SERVER=synscan_cfg.MOTOR_SERVER

def init_wifi():
  global wifi, udp_socket, ble_tx, ble_rx, led_timer
  ble_tx, ble_rx = None, None
  if AP_CHANNEL:
    wifi = network.WLAN(network.AP_IF)
    wifi.active(False)
    wifi.active(True)
    wifi.config(channel=AP_CHANNEL, txpower=17, essid=NAME, password=PASS)
    if DEBUG:
      print(wifi.ifconfig())
  else:
    wifi = network.WLAN(network.STA_IF)
    wifi.active(False)
    wifi.active(True)
    wifi.connect(NAME, PASS)
  while wifi.active() == False:
    pass
  udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  udp_socket.bind(('', 11880))
  led_timer=Timer(0)
  led_timer.init(mode=Timer.PERIODIC, period=1000, callback=led_wifi)

_SO_REGISTER_HANDLER = const(20)

def init_udp_server():
  udp_socket.setsockopt(socket.SOL_SOCKET, _SO_REGISTER_HANDLER, udp_server_recv)

def init_udp_client():
  udp_socket.setsockopt(socket.SOL_SOCKET, _SO_REGISTER_HANDLER, udp_client_recv)

def led_wifi(dummy):
 global wifi_connected, gateway, motorfw
 if wifi.isconnected()==True:
   led(1)
   if(wifi_connected==False):
     if DEBUG:
       print(wifi.ifconfig())
       # ("    IP     ", "   NETMASK   ", "  GATEWAY  ", "    DNS    ")
       # ("192.168.4.2", "255.255.255.0", "192.168.4.1", "192.168.4.1")
   gateway = wifi.ifconfig()[2] # udp_send() to gateway IP
   wifi_connected=True
 else:
   led(0)
   wifi_connected=False

def init_ble():
  global ble
  ble = bluetooth.BLE()
  ble.active(True)
  # ble.config(mtu=512) # doesn't improve
  if DEBUG:
    mac = ble.config('mac')[1].hex().upper()
    print("BLE MAC:",mac)
  disconnected()
  ble.irq(ble_irq)
  register()
  advertiser()

def led(val):
  ledpin.value(val^1)

def connected():
  led(1)

def disconnected():
  led(0)

def wire_autodetect():
  global uart
  for j in range(len(UART_INIT)):
    uart = UART_INIT[j]()
    n = 0 # count succsesful
    a = b""
    for i in range(3):
      wire_rx_flush()
      wire_tx(b":e1\r")
      a = wire_rx()
      if DEBUG:
        print(a)
      if a:
        if a[0]==61: # begins with "=", successful
          # uart works
          n += 1
          if n >= 2: # two successful
            return a
      #  else: # not successful
      #    n = 0 # reset successful
  return a

def wire_rx_flush():
  n=uart.any() # chars available
  if n: # read all available and discard
    uart.read(n)

# read from "=" or "!" to "\r"
def wire_rx():
  r=b""
  for i in range(256): # limit length to max 256 chars
    a=uart.read(1) # 1 char or timeout
    if a: # success
      if a[0]==61: # "="
        r=b"" # reset
      r+=a # append 1 char
      if (r[0]==61 or r[0]==33) and r[-1]==13: # "=...\r" or "!..\r"
        return r
    else: # timeout
      return r
  return r # return at limited length

def wire_tx(data):
  uart.write(data)

def motorfw_select_replace():
  global replace_command, replace_response
  if motorfw in REPLACE:
    replace_command, replace_response = REPLACE[motorfw]
  else:
    replace_command, replace_response = {}, {}

def replace_from_synscan(from_synscan):
  global from_synscan_orig, from_synscan_replace
  from_synscan_orig=from_synscan
  if from_synscan in replace_command:
    from_synscan_replace = replace_command[from_synscan]
  else:
    from_synscan_replace = from_synscan
  return from_synscan_replace

def replace_from_motor(from_motor):
  global motorfw
  if from_motor:
    if from_synscan_replace == b":e1\r":
      if from_motor[0]==61: # response should start with "="
        motorfw = from_motor
        motorfw_select_replace()
      # WiFi mode doesn't like wire_autodetect() here
      #else: # uart autodetect retries ":e1\r"
      #  from_motor = wire_autodetect()
  if from_synscan_orig in replace_response:
    if from_motor in replace_response[from_synscan_orig]:
      from_motor = replace_response[from_synscan_orig][from_motor]
  return from_motor

def wire_txrx(from_synscan):
  if from_synscan:
    wire_rx_flush()
    wire_tx(from_synscan)
    from_motor = wire_rx()
  else:
    from_motor = b""
  return from_motor

def wire_txrx_replace(from_synscan):
  return replace_from_motor(wire_txrx(replace_from_synscan(from_synscan)))

def udp_server_recv(udp):
  led(0)
  request, source = udp.recvfrom(256)
  if request:
    if LOG:
      log.write(request+b"\n")
    response = wire_txrx_replace(request)
    if response:
      udp.sendto(response, source)
      if LOG:
        log.write(response+b"\n")
  led(1)

def udp_client_recv(udp):
  led(0)
  response, source = udp.recvfrom(256)
  response = replace_from_motor(response)
  if response:
    print(response.decode("ASCII"),end="")
    if LOG:
      log.write(response+b"\n")
  led(1)

def ble_irq(event, data):
  if event == 1:
    '''Central connected'''
    connected()
    if LOG:
      log.write(b"connected\n")
  elif event == 2:
    '''Central disconnected'''
    advertiser()
    disconnected()
    if LOG:
      log.write(b"disconnected\n")
      log.flush()
  elif event == 3:
    '''New message received'''
    led(0)
    # method 1 ("True" to notify, faster than method 2)
    request=ble.gatts_read(ble_rx)
    if request:
      if LOG:
        log.write(request+b"\n")
      response=wire_txrx_replace(request)
      if response:
        ble.gatts_write(ble_tx, response, True)
        if LOG:
          log.write(response+b"\n")
    # method 2 (explicitely notify, slower than method 1)
    #conn_handle,_=data
    #ble.gatts_notify(conn_handle, ble_tx, wire_txrx_replace(ble.gatts_read(ble_rx)))
    led(1)

def register():
  global ble_tx, ble_rx
  # Nordic UART Service (NUS)
  #SERVICE_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
  #RX_UUID  = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
  #TX_UUID  = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'

  # synscan_ble serial
  SERVICE_UUID = '0000a002-0000-1000-8000-00805F9B34FB'
  RX_UUID  = '0000c302-0000-1000-8000-00805F9B34FB'
  TX_UUID  = '0000c306-0000-1000-8000-00805F9B34FB'

  BLE_SERVICE = bluetooth.UUID(SERVICE_UUID)
  BLE_RX = (bluetooth.UUID(RX_UUID), bluetooth.FLAG_WRITE)
  BLE_TX = (bluetooth.UUID(TX_UUID), bluetooth.FLAG_NOTIFY)

  BLE_UART = (BLE_SERVICE, (BLE_TX, BLE_RX,))
  SERVICES = (BLE_UART, )
  ((ble_tx, ble_rx,), ) = ble.gatts_register_services(SERVICES)
  ble.gatts_set_buffer(ble_rx, 256, True) # rxbuf 256 bytes for X-commands

def advertiser():
  name = bytearray(NAME, "UTF-8")
  manufacturer_data = b"h.54806524"
  advertise_data = b'\x02\x01\x02' \
    + bytearray((len(name) + 1, 0x09)) \
    + name \
    + bytearray((len(manufacturer_data)+1, 0xFF)) \
    + manufacturer_data
  #print(advertise_data)
  ble.gap_advertise(100, advertise_data)

def usbclient():
  while 1:
    request=input("").encode("ASCII") # input strips "\r"
    if request:
      if LOG:
        log.write(request+b"\r\n")
      if gateway:
        request=replace_from_synscan(request+b"\r")
        if request:
          udp_socket.sendto(request,(gateway,11880))

def usbserial():
  while 1:
    request=input("").encode("ASCII") # input strips "\r"
    if request:
      if LOG:
        log.write(request+b"\r\n")
      response=wire_txrx_replace(request+b"\r")
      if response:
        print(response.decode("ASCII"),end="")
        if LOG:
          log.write(response+b"\n")

ledpin=Pin(PIN_LED, mode=Pin.OUT)
dupterm(None,0) # detach micropython console from tx/rx uart
motorfw=wire_autodetect()
motorfw_select_replace()
gateway=None
if LOG:
  log=open(LOG,"a+")
  log.write("boot\n")
wire_rx_flush()
if WIRELESS:
  if BLE:
    import bluetooth
    init_ble()
  else:
    import network
    import socket
    init_wifi()
    if MOTOR_SERVER:
      init_udp_server()
    else:
      init_udp_client()
      usbclient()
      # Synscan > Settings > Connection Settings > Read Timeout (ms) > 2200 or higher like 3000
else: # directly wired USB-SERIAL
  usbserial()
