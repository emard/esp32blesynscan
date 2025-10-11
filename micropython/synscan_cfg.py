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
  BLE=1 # 0:WiFi 1:BLE

# ESP32
if 0:
  NAME="synscan.py"
  PIN_LED=2 # DevKit LED normal logic
  PIN_RJ12_4_RX_RED=16 # direct
  PIN_RJ12_2_TX_YELLOW_RD=17 # over 10k/BAT42 (but not on board)
  PIN_RJ12_2_TX_YELLOW=17 # direct
  BLE=1 # 0:WiFi 1:BLE

# for Virtuoso Mini FW 2.16.A1
REPLACE_COMMAND_MINI={
# force main encoders
#b":W1040000\r": b":W1050000\r", # rewrite AZ  auxiliary as AZ  main encoder
#b":W2040000\r": b":W2050000\r", # rewrite ALT auxiliary as ALT main encoder
# force auxiliary encoders
#b":W1050000\r": b":W1040000\r", # rewrite AZ  main as AZ  auxiliary encoder
#b":W2050000\r"; b":W2040000\r", # rewrite ALT main as ALT auxiliary encoder
# slow to allow correct counting, 5V operation and quiet
# MANUAL SLEW SPEED: instead slew 9 use slew 8.5
# caution: encoders loose counts with slews faster than 7
b":I1500000\r": b":I1600000\r",
b":I2500000\r": b":I2600000\r",
# GOTO SLEW SPEED
# replace them with slow long goto speed commands
# main AZ  encoders loose counts with < 1C00000
# main ALT encoders loose counts with < 1600000
b":M1AC0D00\r": b":T1C00000\r", # AZ  brake -> AZ  goto speed
b":M2AC0D00\r": b":T2800000\r", # ALT brake -> ALT goto speed
}

# for Virtuoso Mini FW 2.16.A1
REPLACE_RESPONSE_MINI={
# empty
}

# for Virtuoso GTi FW 3.36.AF, 3.40.AF
REPLACE_COMMAND_GTI={
# force main encoders
#b":W1040000\r": b":W1050000\r", # rewrite AZ  auxiliary as AZ  main encoder
#b":W2040000\r": b":W2050000\r", # rewrite ALT auxiliary as ALT main encoder
# force auxiliary encoders
#b":W1050000\r": b":W1040000\r", # rewrite AZ  main as AZ  auxiliary encoder
#b":W2050000\r"; b":W2040000\r", # rewrite ALT main as ALT auxiliary encoder
# SLOW GOTO
b":M1AC0D00\r": b":T1001000\r", # AZ  brake -> AZ  goto speed
b":M2AC0D00\r": b":T2001000\r", # ALT brake -> ALT goto speed
}

# GTi MC014 firmwares 3.36.AF 3.40.AF
# provide wrong counts per AZ/ALT revolution
# :a1 -> =1A330D = 0x0D331A
# :a2 -> =1A330D = 0x0D331A
# az=0° alt=0° and az=180° alt=180° should point to the same
# terrestrial object but they don't, so
# goto az=180° alt=180° and manually pointing
# to the same object, experimentally is found that:
# az=0° alt=0° and az=179°22' alt=176°04' point to the same object, so
# counts per rev az  should be: 0x0D331A*(179+22/60)/180
# counts per rev alt should be: 0x0D331A*(176+ 4/60)/180

# for Virtuoso GTi FW 3.36.AF, 3.40.AF
REPLACE_RESPONSE_GTI={
  b":a1\r": # Inquire counts per revolution of AZ
  {
    b"=1A330D\r": b"="+pack("<I", int(0x0D331A*(179+22/60)/180+0.5))[0:3].hex().encode("utf-8").upper()+b"\r"
  },
  b":a2\r": # Inquire counts per revolution of ALT
  {
    b"=1A330D\r": b"="+pack("<I", int(0x0D331A*(176+ 4/60)/180+0.5))[0:3].hex().encode("utf-8").upper()+b"\r"
  },
}

# Firmware selects replacement of command/response
REPLACE={
  b"=0210A1\r": (REPLACE_COMMAND_MINI, REPLACE_RESPONSE_MINI), # FW 2.16.A1
  b"=0324AF\r": (REPLACE_COMMAND_GTI,  REPLACE_RESPONSE_GTI ), # FW 3.36.AF
  b"=0328AF\r": (REPLACE_COMMAND_GTI,  REPLACE_RESPONSE_GTI ), # FW 3.40.AF
}

# Virtuoso Mini
def uart_half_duplex():
  print("trying half duplex")
  Pin(PIN_RJ12_2_TX_YELLOW, mode=Pin.IN, pull=None)
  return UART(1,baudrate=9600,tx=PIN_RJ12_2_TX_YELLOW_RD,rx=PIN_RJ12_4_RX_RED,timeout=30) # Virtuoso Mini

# Virtuoso GTi
def uart_full_duplex():
  print("trying full duplex")
  Pin(PIN_RJ12_2_TX_YELLOW_RD, mode=Pin.IN, pull=None)
  return UART(1,baudrate=9600,tx=PIN_RJ12_4_RX_RED,rx=PIN_RJ12_2_TX_YELLOW,timeout=30) # Virtuoso GTi

UART_INIT = [uart_half_duplex, uart_full_duplex]
#UART_INIT = [uart_full_duplex,uart_half_duplex]
