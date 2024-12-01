# ESP32 blesyncscan

Arduino ESP32 Bluetooth Classic and Bluetooth Low Energy
UART bridge for SynScan Pro 2.5.2.
UART 3.3V TTL is connected to SkyWatcher Virtuoso 90 Heritage mount.

It works for android, linux and windows.

# Install

Arduino project "btblesynscan" should be used.
It supports both Bluetooth Classic and Bluetooth Low Energy.

From board manager Install esp32 by espressif,
select board "ESP32 Dev Module"

Copy "btblesynscan.ino" to directory "~Arduino/esp32blesynscan/btblesynscan/btblesynscan.ino"

From Arduino, open project "Arduino/esp32blesynscan/btblesynscan",
compile and upload to ESP32 board connected with Micro USB Cable.

# Electrical

There should be 12V->3.3V converter.
To save power recommended is switching converter 
(Canton Power).
RJ-12 plug can't guarantee that GND makes
connection before other pins.
Use 3.6V zener diodes to protect
sensitive 3.3V data pins from getting 12V
during plugging in.

In the mount manual see RJ12 pinout.
Conenct RJ12 RX/TX with short straight
RJ12 cable to ESP32 RX2/TX2 pins.

Mount's serial TTL port is half-duplex
and it seems that mount has hardware
loopback. So everything that is send to
the mount, mount immediately echoes it.

Mount and synscan cannon send at the
same time. If synscan tries to send
while mount sends, then received data
will be just noise.

# Connection

Looking at female RJ-12 socket on the mount:

       ____
    ---    ---
    | 654321 |
    ----------

    1 blue   N.C.
    2 yellow TX       (3.3V) (mount receives)
    3 green  Vpp+     ( 12V)
    4 red    RX       (3.3V) (mount sends)
    5 black  GND
    6 white  Reserved (3.3V)

RX/TX roles on the mount are swapped and
actually indicate RX/TX on remote end.

      mount        esp32
    -----------    ----------
    2 yellow TX    TX2 GPIO17
    4 red    RX    RX2 GPIO16
    5 black  GND   GND

RJ-11 4-pin socket can be used instead of
RJ-12 6-pin because pins 1 and 6 are not connected.

![top](/pic/top.jpg)

![bot](/pic/bot.jpg)

# WARNING WARNING WARNING

There are different RJ-11 and RJ-12 cables,
with [straight and cross wiring](/doc/straight-vs-cross-cable.pdf).
For the telephones it does not matter but here it matters!

STANDARD PHONE CROSS CABLE MAY NOT BE SUITABLE.
USE ONLY STRAIGHT WIRED 4-PIN RJ-11 or
STRAIGHT WIRED 6-PIN RJ-12. CROSS RJ-11 AND RJ-12 
CABLES AND ALL 2-PIN RJ-11 CABLES ARE NOT SUITABLE.
IF A CROSS WIRED CABLE OR ANY 2-PIN CABLE IS CONNECTED
THEN 12V WILL FRY ELECTRONICS IN THE MOUNT AND ESP32.

# Bluetooth Classic or Low Energy

After board power ON or reset by pressing "EN" button,
blue LED will turn ON for 1.5 seconds.

By default if nothing is pressed ESP32 provides
Bluetooth Low Energy Serial.

If "BOOT" button is held during blue LED is ON
then ESP32 will provide Bluetooth Classic Serial.

ESP32 in Bluetooth Low Energy mode only supports
BLE protocol and does not save battery power.
In both Classic and Low Energy modes ESP32 consumes
about 70 mA.

# Android

Synscan works in BLE mode.

SynScan pro -> Settings -> Connect Settings -> BLE.

If device no longer appears in connect list and 
you want to retry connecting, then android application
has to be stopped and started again:

View applications as smaller windows. To stop synscan,
drag it left on ardoid 10 or drag it up on android 14.

Protocol testing:

"Serial Bluetooth Terminal" can connect in
Bluetooth Classic directly when ESP32 is booted
in Bluetooth Classic mode.

"Serial Bluetooth Terminal" can connect in
Low Energy mode with long touch on SynScan_BLE device
selecting "Edit" Custom profile and then
accepting offered UUID values for Service, Read and Write.
Settings:

    Receive Newline = CR
    Send    Newline = Auto (Same as Receive)
    Send    Local Echo ( o) enabled

Basic request/response works:

    request
    :e1\r

    response
    =0210A1\r

# Linux Bluetooth Classic

Bluetooth classic works from linux and
SynScan 2.5.2 pro running under wine,
connecting as serial port.

in shell 1

    hcitool scan
    Scanning ...
            24:0A:C4:11:22:33   SynScan_BT
    rfcomm bind /dev/rfcomm0 24:0A:C4:11:22:33
    unzip synscanpro_windows_252.zip
    cd SynScanPro
    wine SynScanPro.exe
    ... wine will initialize com1 as symlink to /dev/ttyS0
    ... we must change this symlink to /dev/rfcomm0

in shell 2

    cd ~/.wine/dosdevices
    ln -sf /dev/rfcomm0 com1

in SynScan Pro window 

    ... SynScan pro -> Settings -> Connect Settings -> Serial
    ... Serial Port: COM1
    ... press top "<" touch btn then "Connect" btn will appear.
    ... touch "Connect" btn, retry few times

SynScanPro can be debugged from wine:

    winedbg --gdb SynScanPro.exe
    ...
    Wine-gdb> c

# Linux Bluetooth Low Energy

Bluetooth low energy works from linux and
SynScan 2.5.2 pro running under wine,
connecting as serial port.

It works over ble-serial if esp32 is emulating
BLE nRF chip. RN4871 chip emulation will not be
detected by ble-serial.

Install
    
    https://github.com/Jakeler/ble-serial

in shell 1

    source ble-venv/bin/activate
    ble-scan -i hci1
            24:0A:C4:11:22:33   SynScan_BLE
    ble-serial -i hci1 -d 24:0A:C4:11:22:33
    (ble-venv) guest@nuc1:~$ ble-serial -i hci1 -d 24:0A:C4:11:22:33
    23:38:03.521 | INFO | linux_pty.py: Port endpoint created on /tmp/ttyBLE -> /dev/pts/2
    23:38:03.521 | INFO | ble_interface.py: Receiver set up
    23:38:03.741 | INFO | ble_interface.py: Trying to connect with 24:0A:C4:11:22:33: SynScan_BLE
    23:38:05.443 | INFO | ble_interface.py: Device 24:0A:C4:11:22:33 connected
    23:38:05.443 | INFO | ble_interface.py: Found write characteristic 6e400002-b5a3-f393-e0a9-e50e24dcca9e (H. 44)
    23:38:05.443 | INFO | ble_interface.py: Found notify characteristic 6e400003-b5a3-f393-e0a9-e50e24dcca9e (H. 41)
    23:38:05.826 | INFO | main.py: Running main loop!

in shell 2

    cd SynScanPro
    wine SynScanPro.exe
    ... wine will initialize com1 as symlink to /dev/ttyS0
    ... we must change this symlink to /dev/rfcomm0

in shell 3

    cd ~/.wine/dosdevices
    ln -sf /tmp/ttyBLE com1

in SynScan Pro window 

    ... SynScan pro -> Settings -> Connect Settings -> Serial
    ... Serial Port: COM1
    ... press top "<" touch btn then "Connect" btn will appear.
    ... touch "Connect" btn, retry few times

SynScanPro can be debugged from wine:

    winedbg --gdb SynScanPro.exe
    ...
    Wine-gdb> c

# Windows

With suitable BLE adapter, for example TP-LINK UB500
synscan pro 2.5.2 for windows connects with "SynScan_BLE".

"SimplySerial" is simple terminal emulator for
windows. It can can be started from powershell
to print debug messages from esp32.

    ./ss -com:8 -baud:9600
    Connected
    Disconnected

# Principle of operation

ESP32 creates a bluetooth server with serial port bridge.
Phyisical TTL serial port is 9600,8,n,1.

RX Direction synscan->motor (UUID 0xC302)

Bluetooth LE packetizes serial protocol so
entire message is delivered in one packet.
ESP32 filters out some problematic commands for
"2.16.A1" motor firmware (see Firmware bugfix)
other firmwares may not need it.
Message is written to TTL serial and signaled
with "NOTIFY" flow control.

TX Direction motor->synscan (UUID 0xC306)

TTL serial receiver buffers bytes until "complete"
message is received, it begins with '=' or '!'
and ends with '\r'. It is delivered via bluetooth
and signaled with "INDICATE" flow control.

# Firmware bugfix

Motor firmware version 2.16.A1 is the latest but has
problem with SynScan application on android.
After each connect user must enable "Auxiliary Encoder"
otherwise mount will start turning around azimuth axis
and will never stop by itself (user should press cancel to stop).

To fix this in function "udpcb()" one message is rewritten

    :W2050000\r -> :W2040000\r

Second fix is more to prevent sending junk to
motor firmware which is easy to crash.

Synscan sends some AT command probably for its
original SynScan WiFi ESP8266 AT firmware.
This AT command should not reach motor firmware so
"udpcb()" function rewrites this AT command as ":e1\\r"
and to this command motor firmware responds with
version number which is not really response to AT
command but synscan accepts it.

    AT+CWMODE_CUR?\r\n -> :e1\r
