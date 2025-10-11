# micropython >= 1.25

from machine import Pin, UART
from struct import pack

# ESP32S3
if 1:
  NAME="synscan.py"
  PIN_LED=21 # XIAO LED inverse logic
  PIN_RJ12_4_RX_RED=44 # direct
  PIN_RJ12_2_TX_YELLOW_RD=43 # over 10k/BAT42
  PIN_RJ12_2_TX_YELLOW=6 # direct
  SLOW=1 # 5V friendly and quiet
  FORCE_ENC=0 # 0:main/auxiliary 1:main 2:auxiliary
  # FW 2.16.A1 after flashing MC006_Tracking_V0216.MCF
  #FORCE_ENC=2 # FW 2.16.A1 before flashing MC006_Tracking_V0216.MCF
  ENC_SPEED_CTRL=1 # main encoders slow goto, auxiliary encoders fast goto
  # GTi firmware 3.36.AF has wrong counts per revolution, here we fix
  # CPR_AZ = modify response to :a1 - count per revolution of azimuth
  # CPR_ALT = modify response to :a2 - count per revolution of altitude
  #CPR_AZ  = None
  #CPR_ALT = None
  # GTi MC014 firmwares 3.36.AF 3.40.AF ...
  # have wrong counts per AZ/ALT revolution
  # :a1 -> =1A330D = 0x0D331A
  # :a2 -> =1A330D = 0x0D331A
  # az=0° alt=0° and az=180° alt=180° should point to the same
  # terrestrial object but they don't, so after manually pointing
  # them to the same object, experimentally is found that:
  # az=0° alt=0° and az=179°22' alt=176°04' point to the same object, so
  # counts per rev az  should be: 0x0D331A*(179+22/60)/180
  # counts per rev alt should be: 0x0D331A*(176+ 4/60)/180
  # 180°21'
  # 180°9'
  CPR_AZ  = b"="+pack("<I", int(0x0D331A*(179+22/60)/180+0.5))[0:3].hex().encode("utf-8").upper()+b"\r"
  CPR_ALT = b"="+pack("<I", int(0x0D331A*(176+ 4/60)/180+0.5))[0:3].hex().encode("utf-8").upper()+b"\r"
  BLE=1 # 0:WiFi 1:BLE

# ESP32
if 0:
  NAME="synscan.py"
  PIN_LED=2 # DevKit LED normal logic
  PIN_RJ12_4_RX_RED=16 # direct
  PIN_RJ12_2_TX_YELLOW_RD=17 # over 10k/BAT42 (but not on board)
  PIN_RJ12_2_TX_YELLOW=17 # direct
  SLOW=1 # 5V friendly and quiet
  FORCE_ENC=0 # 0:main/auxiliary 1:main 2:auxiliary
  # FW 2.16.A1 after flashing MC006_Tracking_V0216.MCF
  #FORCE_ENC=2 # FW 2.16.A1 before flashing MC006_Tracking_V0216.MCF
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

#UART_INIT = [uart_half_duplex, uart_full_duplex]
UART_INIT = [uart_full_duplex,uart_half_duplex]
