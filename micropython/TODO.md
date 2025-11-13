# TODO

    [x] after disconnect, LED stays ON
    [ ] periodically check uart and autodetect
        if no response
    [x] instead of if/then use dictionary rewrite
        for command and response
    [x] fix half/full duplex autodetection
    [ ] wifi client, log udp traffic to find what is problem
    [ ] W10D8004: W20D8004: are motor power off commands
        no answer to :f1
    [ ] works if timeout set to 2200 ms or higher
    [ ] half/full duplex wrong detection when USB is plugged
        first and then mount powered up
        steps to reproduce
        android and virtuoso mini
        power off mount, plug usb to android,
        power on mount, connnect, goto 10 deg,
        mount will stop responding
        on upper right corner of android circle will start rotating
        further reconnect is not possible because
        android causes something for micropython to exit input loop
        back to repl prompt
        to verify this
        keep mount powered, unplug android, plug PC usb
        mpremote
        press enter and see repl (while it shouldnt)
        >>>
        temporary fix is to force half duplex in synscan_cfg.py
        UART_INIT = [uart_half_duplex]
    [ ] usbserial resets esp32c3
    [ ] if motor server then
        from timer call wire_autodetect() until mount responds
