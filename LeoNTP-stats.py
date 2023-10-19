#
# displays current statistics of the LeoNTP server using private mode 7 request
#
# run as "python LeoNTP-stats-full.py SERVER_NAME"
#

print("## LeoNTP Stats Utility ##")

import socket
import sys
import struct, time
import math
from time import sleep

if len(sys.argv) < 2:
    print("\nError: please specify servername or IP address.\n")
    print("Usage: python LeoNTP-stats.py {server name or IP address}\n")
    sys.exit(1)
    
IPADDR = str(sys.argv[1])	# the only cmd line argument is NTP server address
PORTNUM = 123
VERSION = 4	# NTP version in request
MODE = 7	# mode 7, private

PACKETDATA = bytearray(48)	# current request length is 48 bytes, response is 48 bytes
RX_PACKET = bytearray(100)

PACKETDATA[0] = VERSION << 3 | MODE
PACKETDATA[1] = 0		# sequence
PACKETDATA[2] = 0x10	# implementation == 0x10, custom
PACKETDATA[3] = 1		# request code, only 1 is implemented for now

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
try: 
	RX_PACKET, server = sock.recvfrom(1024)
except:
    print("Unable to contact LeoNTP at " + IPADDR)
    quit()
    

ref_ts0 	=(struct.unpack('<I',RX_PACKET[16:20])[0]) / 4294967296.0	# fractional part of the NTP timestamp
ref_ts1 	= struct.unpack('<I',RX_PACKET[20:24])[0]	# full seconds of NTP timestamp
uptime 		= struct.unpack('<I',RX_PACKET[24:28])[0]
NTP_served 	= struct.unpack('<I',RX_PACKET[28:32])[0]
NTP_dropped	= struct.unpack('<I',RX_PACKET[32:36])[0]
lock_time	= struct.unpack('<I',RX_PACKET[36:40])[0]
#flags 		= struct.unpack( 'B',bytes(RX_PACKET[40]))[0]
numSV 		= struct.unpack( 'B',RX_PACKET[41:42])[0]
ser_num 	= struct.unpack('<H',RX_PACKET[42:44])[0]	
FW_ver      = struct.unpack('<H',RX_PACKET[44:46])[0]
#FW_ver         = struct.unpack('<I',RX_PACKET[44:48])[0]

t = time.gmtime(ref_ts1 - TIME1970)

# actual statistics received from the server
print ("NTP server IP address:", IPADDR)
print ("Server NTP time:", ref_ts1 + ref_ts0)
print ("Server UNIX time:", ref_ts1 - TIME1970)
print ("Server UTC time: %d/%d/%d %02d:%02d:%02f" % (t.tm_mday, t.tm_mon, t.tm_year, t.tm_hour, t.tm_min, t.tm_sec + ref_ts0))
print ("Uptime: %i seconds (%.01f days)" % (uptime, uptime/86400))
print ("NTP requests served:", NTP_served)
print ("NTP packets dropped:", NTP_dropped)
print ("GPS lock time: %i seconds (%.01f days)" % (lock_time, lock_time/86400))
#print ("GPS flags:", flags)
print ("Satellites:", numSV)
print ("Unit S/N:", ser_num)
print ("Firmware Version: " + format(FW_ver>>8, 'x') + "." + format(FW_ver & 0xFF, '02X'))

#derived statistics
print ("Sent:    %.f NTP requests per second" % (1.0 * NTP_served / uptime))
print ("Dropped: %.03f NTP requests per second" % (1.0 * NTP_dropped / uptime))
print ("Frame loss: %.03f percent" % ((100.0 * NTP_dropped)/(NTP_dropped+NTP_served)))

sock.close()
    