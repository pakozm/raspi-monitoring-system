#!/usr/bin/env python2.7
"""This module implements the main program for scheduling the monitoring system.

It should be executed from command line without arguments.
"""
import time
import traceback

import raspi_mon_sys.AEMETMonitor as AEMETMonitor
import raspi_mon_sys.CheckIP as CheckIP
import raspi_mon_sys.ElectricityPricesMonitor as ElectricityPrices
import raspi_mon_sys.LoggerClient as LoggerClient
import raspi_mon_sys.MongoDBHub as MongoDBHub
import raspi_mon_sys.OpenEnergyMonitor as OpenEnergyMonitor
import raspi_mon_sys.PlugwiseMonitor as PlugwiseMonitor
import raspi_mon_sys.Scheduler as Scheduler
import raspi_mon_sys.Utils as Utils

def __try_call(logger, func, *args):
    try:
        return func(*args)
    except:
        print "Unexpected error:",traceback.format_exc()
        logger.error("Unexpected error: %s", traceback.format_exc())
        return None

if __name__ == "__main__":
    Utils.startup_wait()
    
    T1_MILISECOND  = 1
    T1_CENTISECOND = 10
    T1_DECISECOND  = 100
    T1_SECOND      = 1000
    T1_MINUTE      = 60000
    T1_HOUR        = 3600000
    T1_DAY         = 24 * T1_HOUR

    # Configure logger.
    logger = LoggerClient.open("MainMonitoringSystem")

    logger.info("Initializing main monitoring system")

    # Configure Scheduler.
    Scheduler.start()

    logger.info("Scheduler started")

    # Start all modules.
    __try_call(logger, MongoDBHub.start)
    __try_call(logger, AEMETMonitor.start)
    __try_call(logger, CheckIP.start)
    __try_call(logger, ElectricityPrices.start)
    __try_call(logger, OpenEnergyMonitor.start)
    __try_call(logger, PlugwiseMonitor.start)
    
    # repeat every hour with a 1/12th part as offset
    Scheduler.repeat_o_clock_with_offset(T1_HOUR, T1_HOUR/12, MongoDBHub.publish)
    # publish current electricity prices
    __try_call(logger, ElectricityPrices.publish, 0)
    if time.time()*1000 % T1_DAY > 21*T1_HOUR - 10*T1_SECOND:
        # publish next day electricity prices when starting the software at
        # night
        __try_call(logger, ElectricityPrices.publish, 1)
    # publish current IP
    __try_call(logger, CheckIP.publish)
    # publish last AEMET data
    __try_call(logger, AEMETMonitor.publish)

    # repeat every hour AEMET data capture
    Scheduler.repeat_o_clock(T1_HOUR, AEMETMonitor.publish)
    # repeat every time multiple of five minutes (at 00, 05, 10, 15, etc)
    Scheduler.repeat_o_clock(5 * T1_MINUTE, CheckIP.publish)
    # repeat every day at 21:00 UTC with prices for next day
    Scheduler.repeat_o_clock_with_offset(T1_DAY, 21 * T1_HOUR,
                                         ElectricityPrices.publish, 1)
    # repeat every second lectures from plugwise circles
    Scheduler.repeat_o_clock(T1_SECOND, PlugwiseMonitor.publish)

    logger.info("Scheduler configured")
    logger.info("Starting infinite loop")

    # Inifite loop.
    try:
        while True: time.sleep(60)
    except:
        logger.info("Stopping scheduler")
        Scheduler.stop()
        logger.info("Stopping modules")
        __try_call(logger, AEMETMonitor.stop)
        __try_call(logger, CheckIP.stop)
        __try_call(logger, ElectricityPrices.stop)
        __try_call(logger, OpenEnergyMonitor.stop)
        __try_call(logger, PlugwiseMonitor.stop)
        __try_call(logger, MongoDBHub.stop)
        logger.info("Bye!")
