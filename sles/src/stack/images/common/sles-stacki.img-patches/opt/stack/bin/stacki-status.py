#!/opt/stack/bin/python3 -E
#
# @SI_Copyright@
# @SI_Copyright@
#

import socket
import json
import sys

msg = None
if len(sys.argv) > 1:
	msg = sys.argv[1:]

if not msg:
	sys.exit(-1)

sys.path.append('/tmp')
from stack_site import *

health = "health %s" % ' '.join(msg)

tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tx.sendto(health.encode(), (attributes['Kickstart_PrivateAddress'], 5000))
tx.close()
