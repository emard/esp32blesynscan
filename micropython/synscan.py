# micropython >= 1.25

# from linux cmdline:
# mpremote run synscan_ble.py

# from micropython cmdline:
# import synscan_ble

# TODO different speeds for main and auxiliary encoders
# on main encoders request: set slow goto speed
# on auxiliary encoders request: set fast goto speed

from os import dupterm
from machine import Pin, UART, Timer
import synscan_cfg

NAME=synscan_cfg.NAME # BLE client name max 14 chars
PIN_LED=synscan_cfg.PIN_LED # board LED
UART_INIT=synscan_cfg.UART_INIT
AP_CHANNEL=synscan_cfg.AP_CHANNEL
BLE=synscan_cfg.BLE
REPLACE=synscan_cfg.REPLACE
DEBUG=synscan_cfg.DEBUG

def init_wifi():
  global ap, udp_socket, ble_tx, ble_rx, led_timer
  ble_tx, ble_rx = None, None
  ap = network.WLAN(network.AP_IF)
  ap.active(True)
  ap.config(channel=AP_CHANNEL, essid=NAME, password="")
  while ap.active() == False:
    pass
  if DEBUG:
    print(ap.ifconfig())
  # TODO timer irq every 2s call led_wifi()
  udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  udp_socket.bind(('', 11880))
  _SO_REGISTER_HANDLER = const(20)
  udp_socket.setsockopt(socket.SOL_SOCKET, _SO_REGISTER_HANDLER, udp_recv)
  led_timer=Timer(0)
  led_timer.init(mode=Timer.PERIODIC, period=1000, callback=led_wifi)

def led_wifi(dummy):
 if ap.isconnected()==True:
   led(1)
 else:
   led(0)

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
      if len(a):
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

def wire_txrx(from_air):
  global motorfw, goto_az_speed, goto_alt_speed
  if motorfw in REPLACE:
    replace_command, replace_response = REPLACE[motorfw]
  else:
    replace_command, replace_response = {}, {}
  if from_air in replace_command:
    from_air_replace = replace_command[from_air]
  else:
    from_air_replace = from_air
  wire_rx_flush()
  if len(from_air_replace):
    wire_tx(from_air_replace)
    from_wire = wire_rx()
  else:
    from_wire = b""
  if len(from_wire)>0:
    if from_air_replace == b":e1\r":
      if from_wire[0]==61: # response should start with "="
        motorfw = from_wire
      # WiFi mode doesn't like wire_autodetect() here
      #else: # uart autodetect retries ":e1\r"
      #  from_wire = wire_autodetect()
  if from_air in replace_response:
    if from_wire in replace_response[from_air]:
      from_wire = replace_response[from_air][from_wire]
  if DEBUG:
    print(from_air,from_air_replace,from_wire)
  return from_wire

def udp_recv(udp):
  led(0)
  request, source = udp.recvfrom(256)
  if len(request):
    response = wire_txrx(request)
    if len(response):
      udp.sendto(response, source)
  led(1)

def ble_irq(event, data):
  if event == 1:
    '''Central disconnected'''
    connected()
  elif event == 2:
    '''Central disconnected'''
    advertiser()
    disconnected()
  elif event == 3:
    '''New message received'''
    led(0)
    ble.gatts_write(ble_tx, wire_txrx(ble.gatts_read(ble_rx)), True)
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

ledpin = Pin(PIN_LED, mode=Pin.OUT)
dupterm(None,0) # detach micropython console from tx/rx uart
#uart = UART(1,baudrate=9600,tx=43,rx=44,timeout=10) # ESP32S3 virtuoso mini
#uart = UART(1,baudrate=9600,tx=17,rx=16,timeout=10) # ESP32 virtuoso mini
#uart = UART(1,baudrate=9600,tx=PIN_TX,rx=PIN_RX,timeout=TIMEOUT) # ESP32 virtuoso GTi TX/RX swap
motorfw = wire_autodetect()
wire_rx_flush()
# defalut slow goto for ENC_SPEED_CTRL=0
goto_az_speed = b":T1C00000\r"
goto_alt_speed = b":T2800000\r"
if BLE:
  import bluetooth
  init_ble()
else:
  import network
  import socket
  init_wifi()
