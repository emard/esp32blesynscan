# SynScan_BLE Micropython version

The same functionality as arduino but
written in 100 lines of micropython.

It was possible to simplify code logic
because UART always must send someting
to motor hardware to get response. Motor
hardware is otherwise quiet.

So when BLE receives request from synscan,
it sends it over UART and waits timeout of
10ms for UART response. Received response
is sent back to synscan. 

Code doesn't have independent TX and RX threads. 

Response is sligthy slower than arduino
version. It could be because of UART
timeout of 10 ms. But when timeout is set
to less than 10 ms then synscan will not
connect.

install

    mpremote cp synscan_ble.py main.py :/

# Onboard Editor

ESP32 can run small [VT100 terminal editor](https://github.com/robert-hh/Micropython-Editor)

Automatic install from internet using mpremote mip:

    mpremote mip install github:robert-hh/Micropython-Editor
    >>> from pye import pye
