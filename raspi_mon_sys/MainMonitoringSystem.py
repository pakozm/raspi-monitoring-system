#!/usr/bin/env python
#import paho.mqtt.client as paho

import time

import raspi_mon_sys.MailLoggerClient as MailLoggerClient
import raspi_mon_sys.Scheduler as Scheduler

T1_DECISECOND = 0.1
T1_SECOND     = 1
T15_MINUTES   = 60*15
T1_HOUR       = 3600

PAHO_HOST     = "localhost"
PAHO_PORT     = 1883
PAHO_TIMEOUT  = 60

# Configure logger.
logger = MailLoggerClient.open("MainMonitoringSystem")

logger.info("Initializing main monitoring system")

# Configure Paho.
#client = paho.Client()
#client.connect(PAHO_HOST, PAHO_PORT, PAHO_TIMEOUT)
#client.loop_start()

logger.info("Paho initialized at %s:%d with timeout=%d",
            PAHO_HOST, PAHO_PORT, PAHO_TIMEOUT)

# Configure Scheduler.
Scheduler.start()

logger.info("Scheduler started")

Scheduler.repeat_o_clock(T1_HOUR, lambda: logger.info("PING"))
"""More calls to Scheduler for scheduling of other modules..."""

logger.info("Scheduler configured")
logger.info("Starting infinite loop")

# Inifite loop.
try:
    while True: time.sleep(60)
except:
    logger.info("Stopping scheduler")
    Scheduler.stop()
    logger.info("Bye!")
