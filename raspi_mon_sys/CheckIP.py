#!/use/bin/env python
"""This module publishes the IP address using MailLogger.
"""

import socket
import sys
import traceback

from urllib2 import urlopen

import raspi_mon_sys.MailLoggerClient as MailLogger

logger = MailLogger.open("CheckIP")
last_private_ip = None
last_public_ip  = None
failure = False

# This function SHOULD BE implemented always.
def publish():
    """Publishes the IP using an ALERT message."""
    global failure
    global last_public_ip
    global last_private_ip
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        private_ip= s.getsockname()[0]
        s.close()
        public_ip = urlopen('http://ip.42.pl/raw').read()
        if private_ip != last_private_ip or public_ip != last_public_ip:
            logger.alert("My private IP address is %s", private_ip)
            logger.alert("My public IP address is %s", public_ip)
            last_private_ip = private_ip
            last_public_ip  = public_ip
        failure = False
    except:
        print "Unexpected error:", traceback.format_exc()
        if not failure:
            logger.alert("Unable to retrieve IP addresses")
            failure = True
