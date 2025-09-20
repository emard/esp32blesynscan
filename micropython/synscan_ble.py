# micropython >= 1.25

# from linux cmdline:
# mpremote run synscan_ble.py

# from micropython cmdline:
# import synscan_ble

# TODO different speeds for main and auxiliary encoders
# on main encoders request: set slow goto speed
# on auxiliary encoders request: set fast goto speed

from os import dupterm
from machine import Pin, UART
import bluetooth
import synscan_cfg

NAME=synscan_cfg.NAME # BLE client name max 14 chars
PIN_LED=synscan_cfg.PIN_LED # board LED
SLOW=synscan_cfg.SLOW # 1:slow 0:fast
UART_INIT=synscan_cfg.UART_INIT
ALWAYS_AUX_ENC=synscan_cfg.ALWAYS_AUX_ENC
ENC_SPEED_CTRL=synscan_cfg.ENC_SPEED_CTRL

class synscan():

    # name is client name
    def __init__(self, name):
        dupterm(None,0) # detach micropython console from tx/rx uart
        self.ledpin = Pin(PIN_LED, mode=Pin.OUT)
        self.name = name # client name
        #self.uart = UART(1,baudrate=9600,tx=43,rx=44,timeout=10) # ESP32S3 virtuoso mini
        #self.uart = UART(1,baudrate=9600,tx=17,rx=16,timeout=10) # ESP32 virtuoso mini
        #self.uart = UART(1,baudrate=9600,tx=PIN_TX,rx=PIN_RX,timeout=TIMEOUT) # ESP32 virtuoso GTi TX/RX swap
        self.wire_autodetect()
        self.wire_rx_flush()
        self.motorfw = None
        # defalut slow goto for ENC_SPEED_CTRL=0
        self.goto_az_speed = b":T1C00000\r"
        self.goto_alt_speed = b":T2800000\r"
        self.init_ble()

    def init_ble(self):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def led(self,val):
        self.ledpin.value(val^1)

    def connected(self):
        self.led(1)

    def disconnected(self):
        self.led(0)

    def wire_autodetect(self):
      for j in range(len(UART_INIT)):
        self.uart = UART_INIT[j]()
        n = 0 # count succsesful
        for i in range(4):
          self.wire_rx_flush()
          self.wire_tx(b":e1\r")
          a = self.wire_rx()
          # print(a)
          if len(a): # successful
            # uart works
            n += 1
            if n >= 2: # two successful in a row
              return
          else: # not successful
            n = 0 # reset successful

    def wire_rx_flush(self):
      n=self.uart.any() # chars available
      if n: # read all available and discard
        self.uart.read(n)

    # read from "=" or "!" to "\r"
    def wire_rx(self):
      r=b""
      while True:
        a=self.uart.read(1) # 1 char or timeout
        if a: # success
          if a[0]==61: # "="
            r=b"" # reset
          r+=a # append 1 char
          if (r[0]==61 or r[0]==33) and r[-1]==13: # "=...\r" or "!..\r"
            return r
        else: # timeout
          return r

    def wire_tx(self,data):
      self.uart.write(data)

    # return data bytes
    # data_bytes = air_rx()
    def air_rx(self):
      if self.ble_rx: # read from BLE
        return self.ble.gatts_read(self.ble_rx)
      else: # read from wifi
        return b""

    # send data bytes
    # air_tx(bytes)
    def air_tx(self,data):
      if self.ble_tx: # send to BLE
        self.ble.gatts_write(self.ble_tx, data, True)
      else: # send to wifi
        return

    def air_wire_rxtx(self):
      self.led(0)
      from_air = self.air_rx()
      if from_air == b"AT+CWMODE_CUR?\r\n":
          from_air = b":e1\r"
      if self.motorfw == b"=0210A1\r": # Virtuoso Mini
          # if main encoders don't work (firmware bug)
          # to prevent constant azimuth rotation
          # force always using auxiliary encoders
          if ALWAYS_AUX_ENC:
            if from_air == b":W1050000\r": # request for AZ main encoder
              from_air = b":W1040000\r"# rewrite as AZ auxiliary encoder
            if from_air == b":W2050000\r": # request for ALT main encoder
              from_air = b":W2040000\r"# rewrite as ALT auxiliary encoder
          if ENC_SPEED_CTRL:
            if from_air == b":W1050000\r": # request for AZ main encoder
              self.goto_az_speed = b":T1C00000\r"
            if from_air == b":W2050000\r": # request for ALT main encoder
              self.goto_alt_speed = b":T2800000\r"
            if from_air == b":W1040000\r": # request for AZ auxiliary encoder
              self.goto_az_speed = b":T1600000\r"
            if from_air == b":W2040000\r": # request for ALT auxiliary encoders
              self.goto_alt_speed = b":T2600000\r"
          if SLOW:
            # prevent reboots at 5V power
            # MANUAL SLEW SPEED
            # instead of manual slew 9 use slew 8.5
            # warning main encoder looses counts
            # with speeds faster than 6
            if from_air == b":I1500000\r": # AZ
                from_air = b":I1600000\r"
            elif from_air == b":I2500000\r": # ALT
                from_air = b":I2600000\r"
            # GOTO SLEW SPEED
            # M-commands (brake) don't have any effect
            # replace them with slow long goto speed commands
            # main AZ  encoders loose counts with < 1C00000
            # main ALT encoders loose counts with < 1600000
            # auxiliary AZ/ALT encoders can count full speed
            elif from_air == b":M1AC0D00\r": # AZ
                from_air = self.goto_az_speed
            elif from_air == b":M2AC0D00\r": # ALT
                from_air = self.goto_alt_speed
      if self.motorfw == b"=0324AF\r": # Virtuoso GTi
          if SLOW:
            # prevent reboots at 5V power
            # MANUAL SLEW SPEED
            # instead of manual slew 9 use slew 8.5
            if from_air == b":I1C80700\r": # AZ
                from_air = b":I1700000\r"
            elif from_air == b":I2C80700\r": # ALT
                from_air = b":I2700000\r"
            # GOTO SLEW SPEED
            # M-commands (brake) don't have any effect
            # replace them with long goto slew 8.5
            elif from_air == b":M1AC0D00\r": # AZ
                from_air = b":T1700000\r"
            elif from_air == b":M2AC0D00\r": # ALT
                from_air = b":T2700000\r"
      self.wire_rx_flush()
      self.wire_tx(from_air)
      #from_wire = self.uart.read()
      from_wire = self.wire_rx()
      if len(from_wire)>0:
        self.air_tx(from_wire)
        if from_air == b":e1\r":
          self.motorfw = from_wire
      print(from_air,from_wire)
      self.led(1)

    def ble_irq(self, event, data):
        if event == 1:
            '''Central disconnected'''
            self.connected()
        elif event == 2:
            '''Central disconnected'''
            self.advertiser()
            self.disconnected()
        elif event == 3:
            '''New message received'''
            self.air_wire_rxtx()

    def register(self):
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
        ((self.ble_tx, self.ble_rx,), ) = self.ble.gatts_register_services(SERVICES)

    def advertiser(self):
        name = bytearray(self.name, "UTF-8")
        manufacturer_data = b"h.54806524"
        advertise_data = b'\x02\x01\x02' + \
                         bytearray((len(name) + 1, 0x09)) + name + \
                         bytearray((len(manufacturer_data)+1, 0xFF)) + manufacturer_data
        #print(advertise_data)
        self.ble.gap_advertise(100, advertise_data)

# run
synscan = synscan(NAME)
