# micropython UDP server example

# send packet and print response
# echo <packetContent> | socat -t 10 - udp:<dstIp>:<dstPort>,sp:<srcPort>
# echo "abc" | socat -t 10 - udp:192.168.4.1:11880

import network
import socket

def udp_accept(udp):
  # global udp_socket
  print("udp accept")
  # conn, addr = udp_socket.accept()
  request, source = udp.recvfrom(1024)
  print('Content = %s' % str(request))
  response = b"=0210A1\r"
  print("Response = %s" % str(response))
  udp.sendto(response, source)

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="synscan.py", password="")

while ap.active() == False:
  pass

print(ap.ifconfig())

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udp_socket.bind(('', 11880))
_SO_REGISTER_HANDLER = const(20)
udp_socket.setsockopt(socket.SOL_SOCKET, _SO_REGISTER_HANDLER, udp_accept)
