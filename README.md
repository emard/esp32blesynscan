# ESP32 blesyncscan

Arduino ESP32 Bluetooth Classic and Bluetooth Low Energy
UART bridge for SynScan Pro 2.5.2.
UART 3.3V TTL is connected to SkyWatcher Virtuoso 90 Heritage mount.

It works for android and linux, windows not tested yet.

# Install

Arduino project "btblesynscan" is recommended as it
supports both Bluetooth Classic and Bluetooth Low Energy.

From board manager Install esp32 by espressif,
select board "ESP32 Dev Module"

Copy "btblesynscan.ino" to directory "~Arduino/btblesynscan/btblesynscan.ino"

From Arduino, open project "Arduino/btblesynscan",
compile and upload to ESP32 board connected with Micro USB Cable.

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
synscan pro 2.5.2 for windows detects "SynScan_BLE"
adapter but connecting doesn't work with error
"mount mode not detected". ESP32 connected to CP2102
serial port prints "Connected" message after first
BLE connection attempt and when Synscan pro is closed
esp32 prints "Disconnected" message.

"SimplySerial" is simple terminal emulator for
windows. It can can be started from powershell
to print debug messages from esp32.

    ./ss -com:8 -baud:9600
    Connected
    Disconnected

# Android

Synscan works in BLE mode.

"Serial Bluetooth Terminal" can connect in
Bluetooth Classic and Low Energy mode.
Basic request/response works:

    request
    :e1\r

    response
    =0210A1\r
