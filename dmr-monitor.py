#!/usr/bin/env python
#
# Copyright (c) 2013 Cortney T. Buffington, N0MJS and the K0USY Group. n0mjs@me.com
#
# This work is licensed under the Creative Commons Attribution-ShareAlike
# 3.0 Unported License.To view a copy of this license, visit
# http://creativecommons.org/licenses/by-sa/3.0/ or send a letter to
# Creative Commons, 444 Castro Street, Suite 900, Mountain View,
# California, 94041, USA.

import subprocess
import signal
import sys
import os
import socket
import syslog

#-----------------------------
# USER CONFIGURATION
#-----------------------------
DEST_IP = '127.0.0.1'
DEST_PORT = 6667
LOCAL_IP = '127.0.0.1'
DMR_PORT_RANGE = '50000-60000'
#-----------------------------


# Create global variables for the subprocess and it's PID
#
TCPDUMP = ''
PID = ''

# Function to be called if we recieve a termination signal - we have to clean up the child before exit
def handler(_signal, _frame):
    message = 'Terminating proccesses with signal: ' + str( _signal)
    syslog.syslog(syslog.LOG_CRIT, message)
    syslog.closelog()
    os.kill(PID, 15)
    print 'Terminating child proccess with signal:', PID, _signal
    print 'Terminating main process with signal', _signal
    sys.exit()


# Instantiate an object for the subprocess
def start_tcpdump():
    global TCPDUMP, PID
    TCPDUMP = subprocess.Popen(['/usr/local/bin/modtcpdump','-x','-l','-n','-Tdmr','-i','eth0','udp','portrange',DMR_PORT_RANGE,'and','host',LOCAL_IP], stdout=subprocess.PIPE)
    PID = TCPDUMP.pid
    message = 'tcpdump started with PID: ' + str(PID)
    syslog.syslog(syslog.LOG_INFO, message)


# Function to keep seding data from the subprocess as long as it's alive
def send_data():
    while TCPDUMP.poll() != 0:
        line = TCPDUMP.stdout.readline()
        my_socket.sendto(line, (DEST_IP, DEST_PORT))
    message = 'tcpdump has terminated. PID: ' + str(PID)
    syslog.syslog(syslog.LOG_ERR, message)


if __name__ == '__main__':

    syslog.openlog('DMR-Monitor')
    message = 'Program Invoked as: ' + sys.argv[0]
    syslog.syslog(syslog.LOG_INFO, message)

    # Set signal handers so that we can gracefully exit if need be
    for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
        signal.signal(sig, handler)

    # Create our socket
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Main program loop - if tcpdump dies, restart it and keep going...
    while True:
        start_tcpdump()
        send_data()
