# micropython >= 1.25

# from linux cmdline:
# mpremote run synscan_ble.py

# from micropython cmdline:
# import synscan_ble

from os import dupterm
from machine import Pin, UART
import bluetooth
import synscan_cfg

NAME=synscan_cfg.NAME # BLE client name max 14 chars
PIN_LED=synscan_cfg.PIN_LED # board LED
SLOW=synscan_cfg.SLOW # 1:slow 0:fast
UART_INIT=synscan_cfg.UART_INIT

class BLE():

    def __init__(self, name):
        dupterm(None,0) # detach micropython console from tx/rx uart
        self.ledpin = Pin(PIN_LED, mode=Pin.OUT)
        self.name = name
        #self.uart = UART(1,baudrate=9600,tx=43,rx=44,timeout=10) # ESP32S3 virtuoso mini
        #self.uart = UART(1,baudrate=9600,tx=17,rx=16,timeout=10) # ESP32 virtuoso mini
        #self.uart = UART(1,baudrate=9600,tx=PIN_TX,rx=PIN_RX,timeout=TIMEOUT) # ESP32 virtuoso GTi TX/RX swap
        self.uart_autodetect()
        self.read_flush()
        self.motorfw = None
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

    def uart_autodetect(self):
      for j in range(len(UART_INIT)):
        self.uart = UART_INIT[j]()
        n = 0
        for i in range(3):
          self.read_flush()
          self.uart.write(b":e1\r")
          a = self.uart.read()
          print(a)
          if a:
            if a.find(b"=")>=0: # response contains "=" -> uart works
              n += 1
              if n >= 2:
                return

    def read_flush(self):
      n=self.uart.any() # chars available
      if n: # read all available and discard
        self.uart.read(n)

    # read from "=" to "\r"
    def read_eq_cr(self):
      r=b""
      while True:
        a=self.uart.read(1) # 1 char or timeout
        if a: # success
          if a[0]==61: # "="
            r=b"" # reset
          r+=a # append 1 char
          if r[0]==61 and r[-1]==13: # "=...\r"
            return r
        else: # timeout
          return r

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
            self.led(0)
            from_ble = self.ble.gatts_read(self.rx)
            if from_ble == b"AT+CWMODE_CUR?\r\n":
                from_ble = b":e1\r"
            if self.motorfw == b"=0210A1\r":
                # prevent constant azimuth rotation
                # force always using AZ AUX encoders
                if from_ble == b":W2050000\r":
                    from_ble = b":W2040000\r"
                if SLOW:
                  # prevent reboots at 5V power
                  # MANUAL SLEW SPEED
                  # instead of manual slew 9 use slew 8.5
                  if from_ble == b":I1500000\r": # AZ
                      from_ble = b":I1600000\r"
                  elif from_ble == b":I2500000\r": # ALT
                      from_ble = b":I2600000\r"
                  # GOTO SLEW SPEED
                  # M-commands (brake) don't have any effect
                  # replace them with long goto slew 8.5
                  elif from_ble == b":M1AC0D00\r": # AZ
                      from_ble = b":T1600000\r"
                  elif from_ble == b":M2AC0D00\r": # ALT
                      from_ble = b":T2600000\r"
            self.read_flush()
            self.uart.write(from_ble)
            #from_uart = self.uart.read()
            from_uart = self.read_eq_cr()
            if len(from_uart)>0:
              self.ble.gatts_write(self.tx, from_uart, True)
              if from_ble == b":e1\r":
                self.motorfw = from_uart
            print(from_ble,from_uart)
            self.led(1)

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
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)

    #def send(self, data):
    #    self.ble.gatts_notify(0, self.tx, data)

    def advertiser(self):
        name = bytearray(self.name, "UTF-8")
        manufacturer_data = b"h.54806524"
        advertise_data = b'\x02\x01\x02' + \
                         bytearray((len(name) + 1, 0x09)) + name + \
                         bytearray((len(manufacturer_data)+1, 0xFF)) + manufacturer_data
        #print(advertise_data)
        self.ble.gap_advertise(100, advertise_data)

# run
ble = BLE(NAME)
