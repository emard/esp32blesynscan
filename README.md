# ESP32 blesyncscan

Attempt to make ESP32 BLE UART bridge that can be used
to connect SynScan Pro 2.5.2 on Android 10 phone with
SkyWatcher Virtuoso 90 Heritage mount.

Currently "Serial Bluetooth Terminal" can connect and
basic request/response works:

    request
    :e1\r

    response
    =0210A1\r

But synscan pro application when set connection as BLE
and then touch "Connect" button displays "Searching" and
"Device Not Found".
