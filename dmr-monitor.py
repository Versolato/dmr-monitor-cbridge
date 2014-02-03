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
import ConfigParser
import optparse


# Create global variables
#
TCPDUMP = ''
PID = ''
CONFIG_DIR = '/usr/local/etc'
CONFIG_FILE = 'dmr-monitor-config.py'

parser = optparse.OptionParser()
parser.add_option('-c', '--config', action='store', dest='CFG_FILE', help='/full/path/to/config.file (usually dmr-monitor.cfg)')

(cli_args, args) = parser.parse_args()
config = ConfigParser.ConfigParser()

if not cli_args.CFG_FILE:
    cli_args.CFG_FILE = '/usr/local/etc/dmr-monitor.cfg'
try:
    if not config.read(cli_args.CFG_FILE):
        sys.exit('Configuration file \''+cli_args.CFG_FILE+'\' is not a valid configuration file! Exiting...')        
except:    
    sys.exit('Configuration file \''+cli_args.CFG_FILE+'\' is not a valid configuration file! Exiting...')

try:
    for section in config.sections():
        if section == 'CONFIG':
            DEST_IP = config.get(section, 'DEST_IP')
            DEST_PORT = config.getint(section, 'DEST_PORT')
            LOCAL_IP = config.get(section, 'LOCAL_IP')
            DMR_PORT_RANGE = config.get(section, 'DMR_PORT_RANGE')
except:
    sys.exit('Could not parse configuration file, exiting...')


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
    for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGQUIT, signal.SIGKILL]:
        signal.signal(sig, handler)

    # Create our socket
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Main program loop - if tcpdump dies, restart it and keep going...
    while True:
        start_tcpdump()
        send_data()
