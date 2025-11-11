# SynScan_BLE Micropython version

300 lines of micropython replace
parts of synscan protocol on transmit
and receive side to:

Slow speed for encoders to reliably
track position without loosing counts.

Fine tune counts per revolution.
turning both axes for 180° should
point to the same point as 0°.

Fake version number for synscan
to avoid using long X-commands.

# BLE Motor Server

Primary use is for android. Mount lacks BLE support and
using WiFi is not practical.

BLE connects in few seconds, works stable and reliable.
WiFi on android is free to be used for internet
access or camera.

Works on ESP32, ESP32S3, ESP32C3.

When BLE receives request from synscan,
it sends it over UART and waits timeout of
10ms for UART response. Received response
is sent back to synscan. 

UART should send someting to motor hardware
to get response. Motor hardware is otherwise quiet.

# WiFi to USB-Serial Motor Client

Primary use is for linux.
Linux currently lacks good BLE-serial support.
ESP32 connects to remoute mount using WiFi
and modifies protocol to fix issues.

Works on ESP32, ESP32C3.

SynScan Pro works under wine and it can use Serial to connect.

To find out which serial port on wine is for synscan:

    ls -al ~/.wine/dosdevices
    lrwxrwxrwx 1 user user   12 Oct  10 23:52 com5 -> /dev/ttyACM0

Port is COM5 - it can vary.

Set Serial Read Timeout to 2200 ms or
higher like 3000 or 5000 ms. When connect to
serial starts probably DTR is toggled so ESP32C3
is restarted and the read timeout should be long
enough for ESP32C3 to connect to mount WiFi.

    Synscan > Settings > Connection Settings > Read Timeout (ms) > 2200 or higher like 3000

# Install

    mpremote cp synscan_cfg.py synscan.py main.py :/

# Onboard Editor

ESP32 can run small [VT100 terminal editor](https://github.com/robert-hh/Micropython-Editor)

Automatic install from internet using mpremote mip:

    mpremote mip install github:robert-hh/Micropython-Editor
    >>> from pye import pye

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
