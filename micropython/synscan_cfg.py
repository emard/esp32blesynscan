# micropython >= 1.25

# ESP32S3 Virtuoso Mini
if 1:
  NAME="Virtuoso_Mini"
  PIN_LED=21 # XIAO LED inverse logic
  PIN_TX=43 # 10k/BAT42 to RJ-12 pin 2 yellow
  PIN_RX=44 # direct to RJ-12 pin 4 red
  TIMEOUT=30 # [ms]
  CANCEL_ECHO=1 # 1 for mini
  SLOW=1 # 5V friendly and quiet

# ESP32S3 Virtuoso GTi
if 0:
  NAME="Virtuoso_GTi"
  PIN_LED=21 # XIAO LED inverse logic
  PIN_TX=44 # direct to RJ-12 pin 4 red
  PIN_RX=6 # direct to RJ-12 pin 2 yellow
  TIMEOUT=30 # [ms]
  CANCEL_ECHO=0 # 0 for GTi
  SLOW=0 # 12V fast

# ESP32 Virtuoso Mini
if 0:
  NAME="Virtuoso_Mini"
  PIN_LED=2 # DevKit LED normal logic
  PIN_TX=17 # 10k/BAT42 to RJ-12 pin 2 yellow
  PIN_RX=16 # direct to RJ-12 pin 4 red
  TIMEOUT=30 # [ms]
  CANCEL_ECHO=1 # 1 for mini
  SLOW=1 # 5V friendly and quiet

# ESP32 Virtuoso GTi
if 0:
  NAME="Virtuoso_GTi"
  PIN_LED=2 # DevKit LED normal logic
  PIN_TX=16 # direct to RJ-12 pin 4 red
  PIN_RX=17 # direct to RJ-12 pin 2 yellow
  TIMEOUT=30 # [ms]
  CANCEL_ECHO=0 # 0 for GTi
  SLOW=0 # 12V fast
