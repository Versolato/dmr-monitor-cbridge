dmr-monitor-cbridge
===================

A small package for sniffing DMR header information from a c-Bridge and forwarding it to a logging server

About:
This package is targetted and tested specifically for the Ravennet/Rayfield
Communications c-Bridge IPSC version 7456, but should work as long as the
underlying CentOS version remains mostly intact. Note, the c-Bridge is
currently built on CentOS 5.2 and includes a rather old version of Python.
This program works with the installed Python verison and modules, and 
thus requires *NO MODIFICATAIONS* to the c-Bridge. Likewise, a pre-complied
binary of tcpdump called "modtcpdump" is included (thanks Hans Juergen, DL5DI)
that can decode several DMR protocol fields. As this is a pre-compiled binary,
it does not require any changes to the c-Bridge environment.

Manifest:
README: This file.
modtcpdump: A modified tcpdump with DMR extensions.
dmrdump: A shell script useful for debugging, just execute it.
dmr-monitor.py: Python program to gather data and send it to a server

Installation:
Copy modtcpdump, dmrdump and dmr-monitor.py to /usr/local/bin and ensure they are
owned by root and executable. You will need to be root to run dmrdump directly,
so either use sudo or su if you're not logged in as root already... a poor
practice, but the typical way the CLI is accessed on a c-Bridge.

Configuration:
There are only a few parameters that need changed for your local configuration and
must be changed in dmr-monitor.py itself, they are:

    DEST_IP = '176.10.105.232'
    DEST_PORT = 51557
    LOCAL_IP = '192.168.65.50'
    DMR_PORT_RANGE = '50000-60000'

Destination IP and Port are for the server you wish to send your data to. LOCAL_IP
and DMR_PORT_RANGE are sanity checks for modtcpdump. The local IP should be the
eth0 IP address of your c-Bridge, and DMR_PORT_RANGE should include all of the 
UDP ports in use by your DMR network(s)

For Automatic Operation:
Add the following line to the end of /etc/rc.local to start and background this
program at system start.

    /usr/local/bin/dmr-monitor.py > /dev/null 2>&1 &


dmr-monitor.py:
Copyright (c) 2013 Cortney T. Buffington, N0MJS and the K0USY Group. n0mjs@me.com
This work is licensed under the Creative Commons Attribution-ShareAlike
3.0 Unported License.To view a copy of this license, visit
http://creativecommons.org/licenses/by-sa/3.0/ or send a letter to
Creative Commons, 444 Castro Street, Suite 900, Mountain View,
California, 94041, USA.

Included in this package is a binary of tcpdump, with extentions for DMR protocol
Decoding. These are included with the our thanks to the authors

base tcpdump code:
  Copyright (c) 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 2000
 	The Regents of the University of California.  All rights reserved.

Incremental modifications to tcpdump are copyright (c) their respective owners;
a great number of people who have made immeasurable contributions over the years

DMR modifications to tcpdump is copyright (c) Hans Juergen, DL5DI
