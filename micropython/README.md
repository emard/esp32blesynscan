# SynScan_BLE Micropython version

The same functionality as arduino but
written in 200 lines of micropython.

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
