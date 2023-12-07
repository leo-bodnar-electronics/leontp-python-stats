#
# displays current statistics of the LeoNTP server using private mode 7 request
#
# run as "python LeoNTP-location.py SERVER_NAME"
#

print("## LeoNTP Location Utility ##")

import socket
import sys
import struct, time
import math
from time import sleep

if len(sys.argv) < 2:
    print("\nError: please specify servername or IP address.\n")
    print("Usage: python LeoNTP-location.py {server name or IP address}\n")
    sys.exit(1)
    
IPADDR = str(sys.argv[1])	# the only cmd line argument is NTP server address
PORTNUM = 123
VERSION = 4	# NTP version in request
MODE = 7	# mode 7, private

PACKETDATA = bytearray(48)	# current request length is 48 bytes, response is 48 bytes
RX_PACKET = bytearray(100)

#First check for the version to be correct
PACKETDATA[0] = VERSION << 3 | MODE
PACKETDATA[1] = 0		# sequence
PACKETDATA[2] = 0x10	# implementation == 0x10, custom
PACKETDATA[3] = 1		# request code, only 1 is implemented for now

PACKETDATA[4] = 0		# unused for now
PACKETDATA[5] = 0
PACKETDATA[6] = 0
PACKETDATA[7] = 0


######################

# Create a UDP socket
server_address = (IPADDR, 123)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.5)

# Send request
sent = sock.sendto(PACKETDATA, server_address)
sent = sock.sendto(PACKETDATA[0:8], server_address)

# Receive response
try: 
	RX_PACKET, server = sock.recvfrom(1024)
except:
    print("Unable to contact LeoNTP at " + IPADDR)
    quit()


FW_ver      = struct.unpack('<H',RX_PACKET[44:46])[0]
FW_ver_major = FW_ver >> 8;
FW_ver_minor = FW_ver & 0xff;


if (FW_ver_major < 2 or FW_ver_minor < 6):
	print("Invalid Firmware Version: " + format(FW_ver_major, '02X') + "." +  format(FW_ver_minor, '02X'))
	print("Must be at least 2.06")
	sock.close()
	quit()

sock.close()

#Location Retrieval

PACKETDATA[0] = VERSION << 3 | MODE
PACKETDATA[1] = 0		# sequence
PACKETDATA[2] = 0x10	# implementation == 0x10, custom
PACKETDATA[3] = 2		# request code, only 1 is implemented for now

PACKETDATA[4] = 0		# unused for now
PACKETDATA[5] = 0
PACKETDATA[6] = 0
PACKETDATA[7] = 0

# reference time (in seconds since 1900-01-01 00:00:00) for conversion from NTP time to system time
TIME1970 = 2208988800

# Create a UDP socket
server_address = (IPADDR, 123)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.5)

# Send request
sent = sock.sendto(PACKETDATA, server_address)
sent = sock.sendto(PACKETDATA[0:8], server_address)

# Receive response
# Receive response
try: 
	RX_PACKET, server = sock.recvfrom(1024)
except:
    print("Unable to contact LeoNTP at " + IPADDR)
    quit()


print (RX_PACKET)
print ("\n\n")
print (','.join([hex(i) for i in RX_PACKET]))

lon 		= struct.unpack('<i',RX_PACKET[16:20])[0] / 10000000.0
lat 		= struct.unpack('<i',RX_PACKET[20:24])[0] / 10000000.0
hMSL 		= struct.unpack('<i',RX_PACKET[24:28])[0] / 1000.0

print ("Longitude:  ", lon)
print ("Latitude:   ", lat)
print ("Height MSL: ", hMSL)

sock.close()
    
