# SynScan_BLE Micropython version

300 lines of micropython replace
parts of synscan protocol on transmit
and receive side to:

Slow speed for encoders to reliably
track position without loosing counts.

Fine tune counts per revolution.
Turning both axes for 180° should
point to the same object as 0°.

Fake version number for synscan
to avoid using long X-commands.

# Install

    mpremote cp synscan_cfg.py synscan.py main.py :/

# Configure

Almost everything is configurable. Edit

    synscan_cfg.py

Using your favourite text editor on PC.
ESP32 has good editor written in micropython.

# Onboard Editor

ESP32 can run small [VT100 terminal editor](https://github.com/robert-hh/Micropython-Editor)

Automatic install from internet using mpremote mip:

    mpremote mip install github:robert-hh/Micropython-Editor

Edit config file:

    >>> from pye import pye
    >>> pye("synscan_cfg.py")

quick editor help

    ctrl-q        quit
    ctrl-s        save
    backspace     delete left of cursor
    arrows        move cursor
    shift-arrows  select block
    del           delete selected block
    ctrl-c        copy   selected block
    ctrl-v        paste  selected block
    ctrl-e        redraw screen

Troubleshooting

ESP32-WROOM and ESP32C3 dont have PSRAM so
memory is tight. After "import synscan"
there will be not enough free memory to
load editor:

    >>> from pye import pye
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    MemoryError: memory allocation failed, allocating 285 bytes

workaround: Get micropython prompt with ctrl-c, then
while holding ctrl type quickly "dccc" to soft reboot
and immediately interrupt "main.py" before
"import synscan". It should be possible to
load editor then:

    ctrl-c
    ...
    >>>
    ctrl-dccc
    ...
    >>> from pye import pye
    >>> pye("synscan_cfg.py")

# BLE Motor Server

Primary use is for Android. Works on Windows.
Linux BLE-serial written in python doesn't work.
Mount lacks BLE support and using its WiFi
is not practical, complicated routing etc.

BLE connects in few seconds, works stable and reliable.
WiFi on android is free to be used for internet
access or camera.

Works on ESP32, ESP32S3, ESP32C3.

When BLE receives request from synscan,
it sends it over UART and waits some timeout 30 ms or 200 ms
for UART response. Received response
is sent back to synscan. 

UART should send someting to motor hardware
to get response. Motor hardware is otherwise quiet.

# WiFi Motor Server

Primary use is to make additional networking
connectivity and compatibility. It can be WiFi
client while mount is WiFi Server.

Works on ESP32, ESP32C3.

To print IP

    synscan.wifi.ifconfig()

Currently it doesn't work reliable on ESP32S3.
Multiple retries required to connect. Packet loss
and timeout too long to be practical (30 seconds).

# WiFi to USB-Serial Motor Client

Primary use is for linux. Works on Windows and Android too.
Linux BLE-serial written in python doesn't work so this USB
to WiFi bridge is very practical.
ESP32 connects to mount using WiFi
and modifies protocol to fix issues.

Works on ESP32, ESP32S3, ESP32C3 (wine reboots ESP32C3).
Micropython versions from 1.23.0 to 1.26.1 have been
tried but ESP32S3 doesn't connect to WiFi.

Android: SynScan Pro connects with default serial settings

    SynScan Pro > Settings > Connection Settings > Serial

Linux: SynScan Pro works under wine when you find COM port
and set serial read timeout to 3-5 seconds.

To find out which serial port on wine is for synscan:

    ls -al ~/.wine/dosdevices
    lrwxrwxrwx 1 user user   12 Oct  10 23:52 com5 -> /dev/ttyACM0

Port is COM5 (last number can vary).

Wine SynScan Pro needs increased serial parameters to connect:

    Resend Tries * Serial Read Timeout > 9 seconds

ESP32S3 connects with default serial timeouts.

ESP32C3 needs increased serial timeouts.
When Synscan initiates connection to serial port it
probably toggles DTR or does something to serial port
which causes ESP32C3 to restart.
Read timeout should be long enough for
ESP32C3 to boot and connect to mount WiFi.

    SynScan Pro > Settings > Connection Settings > Serial
    SynScan Pro > Settings > Connection Settings > Resend Tries      > 2
    SynScan Pro > Settings > Connection Settings > Read Timeout (ms) > 5000

or

    SynScan Pro > Settings > Connection Settings > Serial
    SynScan Pro > Settings > Connection Settings > Resend Tries      > 10
    SynScan Pro > Settings > Connection Settings > Read Timeout (ms) > 1000

# Direct Wire USB-Serial Motor Client

Works on Windows, Android, Linux.
Works on ESP32, ESP32S3, ESP32C3 (wine reboots ESP32C3).
Similar as WiFi to USB-Serial Motor Client.

# Troubleshooting

Virtuoso Mini with MC006:

According to
[BDN at Cloudy Nights](https://www.cloudynights.com/topic/941083-skywatcher-heritage-90-virtuoso-synscan-pro-compatibility/)
this bug can be fixed by making USB-SERIAL adapter and flashing firmware
[MC006_Tracking_V0216.MCF](https://stargazerslounge.com/topic/336944-firmware-for-the-virtuoso-skywatcher/)
posted by Antoine1997 at Stargazer's Lounge.

Virtuoso GTi with MC014:

Flash firmware 3.40.AF but and synscan_cfg.py has
appropriate fixes, this includes slowing down manual
and goto slew, adjusting number of pulses per revolution
and rewriting firmware version to 3.36.AF to avoid using
of new X-commands.

CPU of MC014 misses encoder pulses, it is probably because
interrupt is used to count pulses instead of using hardware
counting like PCNT on ESP32 which may also be available on ESP8266.
which is mounted on MC014 PCB.

Best is to avoid switching to aux controllers during first 15 minutes,
while WiFi LED on the mount is blinking.
After 15 minutes WiFi LED will turn ON constantly, WiFi will be
off and interrupts will have more chance to catch encoder pulses.
so then it is good time to try aux encoders.

Encoders will then correctly work when synscan commands are send
from application to the mount and mount is moving slow according
to synscan_cfg.py slew speed setup.

But when clutches are released for manually pointing telescope
aka "Freedom Find" mode then aux controllers will start
loosing counts and that means that "Freedom Find" actually
doesn't work for MC014 hardware with currently tried firmwares
3.36.AF and 3.40.AF.
