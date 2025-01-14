# micropython >= 1.25

# from linux cmdline:
# mpremote run synscan_ble.py

# from micropython cmdline:
# import synscan_ble

from os import dupterm
from machine import Pin, UART
import bluetooth

LED_PIN=21 # XIAO LED inverse logic

class BLE():

    def __init__(self, name):
        dupterm(None,0) # detach micropython console from tx/rx uart
        self.name = name
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ledpin = Pin(LED_PIN, Pin.OUT)
        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()
        self.uart = UART(1,baudrate=9600,tx=43,rx=44,timeout=10)
        self.motorfw = None

    def led(self,val):
        self.ledpin.value(val^1)

    def connected(self):
        self.led(1)

    def disconnected(self):
        self.led(0)

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
                if from_ble == b":W2050000\r":
                    from_ble = b":W2040000\r"
            self.uart.write(from_ble)
            from_uart = self.uart.read()
            if from_uart:
              # cancel echo: response starts after first "\r"
              from_uart = from_uart[from_uart.find(b"\r")+1:]
              self.ble.gatts_write(self.tx, from_uart, True)
              if from_ble == b":e1\r":
                self.motorfw = from_uart
            print(from_ble,from_uart)
            self.led(1)

    def register(self):
        # Nordic UART Service (NUS)
        #NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        #RX_UUID  = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        #TX_UUID  = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'

        # synscan_ble serial
        NUS_UUID = '0000a002-0000-1000-8000-00805F9B34FB'
        RX_UUID  = '0000c302-0000-1000-8000-00805F9B34FB'
        TX_UUID  = '0000c306-0000-1000-8000-00805F9B34FB'

        BLE_NUS = bluetooth.UUID(NUS_UUID)
        BLE_RX = (bluetooth.UUID(RX_UUID), bluetooth.FLAG_WRITE)
        BLE_TX = (bluetooth.UUID(TX_UUID), bluetooth.FLAG_NOTIFY)

        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        self.ble.gatts_notify(0, self.tx, data + '\n')

    def advertiser(self):
        name = bytearray(self.name, 'UTF-8')
        manufacturer_data=bytearray("h.54806524", "UTF-8")
        advertise_data = bytearray('\x02\x01\x02', 'UTF-8') + \
                         bytearray((len(name) + 1, 0x09)) + name + \
                         bytearray((len(manufacturer_data)+1, 0xFF)) + manufacturer_data
        #print(advertise_data)
        self.ble.gap_advertise(100, advertise_data)

# run
ble = BLE("synscan_ble.py")