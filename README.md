# ESP32 blesyncscan

Arduino ESP32 Bluetooth Classic and Bluetooth Low Energy
UART bridge for SynScan Pro 2.5.2.
UART 3.3V TTL is connected to SkyWatcher Virtuoso 90 Heritage mount.

Currently it works for linux.
Hopfully with small fixes it should work on Android 10 phone.

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
Bluetooth Classic Serial.

If "BOOT" button is held during blue LED is ON
then ESP32 will provide Bluetooth Low Energy Serial.

ESP32 in Bluetooth Low Energy mode only supports
BLE protocol and does not save battery power.
In both Classic and Low Energy modes ESP32 consumes
about 70 mA.

# Linux

Bluetooth classic works from linux and
SynScan 2.5.2 pro running under wine.

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

# Android

Currently "Serial Bluetooth Terminal" can connect in
Bluetooth Classic and Low Energy mode.
Basic request/response works:

    request
    :e1\r

    response
    =0210A1\r

But synscan pro application when set connection as BLE
and then touch "Connect" button displays "Searching" and
"Device Not Found".
