# micropython >= 1.25

from machine import Pin, UART

# ESP32S3
if 1:
  NAME="synscan.py"
  PIN_LED=21 # XIAO LED inverse logic
  PIN_RJ12_4_RX_RED=44 # direct
  PIN_RJ12_2_TX_YELLOW_RD=43 # over 10k/BAT42
  PIN_RJ12_2_TX_YELLOW=6 # direct
  SLOW=1 # 5V friendly and quiet
  ALWAYS_AUX_ENC=0 # FW 2.16.A1 after flashing MC006_Tracking_V0216.MCF
  #ALWAYS_AUX_ENC=1 # FW 2.16.A1 before flashing MC006_Tracking_V0216.MCF
  ENC_SPEED_CTRL=1 # main encoders slow goto, auxiliary encoders fast goto
  BLE=1 # 0:WiFi 1:BLE

# ESP32
if 0:
  NAME="synscan.py"
  PIN_LED=2 # DevKit LED normal logic
  PIN_RJ12_4_RX_RED=16 # direct
  PIN_RJ12_2_TX_YELLOW_RD=17 # over 10k/BAT42 (but not on board)
  PIN_RJ12_2_TX_YELLOW=17 # direct
  SLOW=1 # 5V friendly and quiet
  ALWAYS_AUX_ENC=0 # allow switcing main/auxiliary encoders
  ENC_SPEED_CTRL=0 # same goto speed for main and auxiliary encoders
  BLE=1 # 0:WiFi 1:BLE

# Virtuoso Mini
def uart_half_duplex():
  Pin(PIN_RJ12_2_TX_YELLOW, mode=Pin.IN, pull=None)
  return UART(1,baudrate=9600,tx=PIN_RJ12_2_TX_YELLOW_RD,rx=PIN_RJ12_4_RX_RED,timeout=30) # Virtuoso Mini

# Virtuoso GTi
def uart_full_duplex():
  Pin(PIN_RJ12_2_TX_YELLOW_RD, mode=Pin.IN, pull=None)
  return UART(1,baudrate=9600,tx=PIN_RJ12_4_RX_RED,rx=PIN_RJ12_2_TX_YELLOW,timeout=30) # Virtuoso GTi

UART_INIT = [uart_half_duplex, uart_full_duplex]
