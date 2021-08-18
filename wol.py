# -*- coding: utf-8 -*-
"""
Based on wol.py from http://code.activestate.com/recipes/358449-wake-on-lan/
Amended to use configuration file and hostnames

Copyright (C) Fadly Tabrani, B Tasker

Released under the PSF License See http://docs.python.org/2/license.html
"""


import socket
import struct
import os
import sys
import configparser
import re

my_config = {}


def wake_on_lan(host):
    """Switches on remote computers using WOL."""
    global my_config

    try:
        mac_address = my_config[host]['mac']
    except KeyError:
        return False

    # Check mac address format
    found = re.fullmatch(
        '^([A-F0-9]{2}(([:][A-F0-9]{2}){5}|([-][A-F0-9]{2}){5})|([s][A-F0-9]{2}){5})|([a-f0-9]{2}(([:][a-f0-9]{2}){'
        '5}|([-][a-f0-9]{2}){5}|([s][a-f0-9]{2}){5}))$',
        mac_address)
    # We must found 1 match , or the MAC is invalid
    if found:
        # If the match is found, remove mac separator [:-\s]
        mac_address = mac_address.replace(mac_address[2], '')
    else:
        raise ValueError('Incorrect MAC address format')

    # Pad the synchronization stream.
    data = ''.join(['FFFFFFFFFFFF', mac_address * 20])
    send_data = b''

    # Split up the hex values and pack.
    for j in range(0, len(data), 2):
        send_data = b''.join([
            send_data,
            struct.pack('B', int(data[j: j + 2], 16))
        ])

    # Broadcast it to the LAN.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(send_data, (my_config['General']['broadcast'], 7))
    return True


def load_config():
    """Read in the Configuration file to get CDN specific settings."""
    global my_dir
    global my_config
    config = configparser.ConfigParser()
    config.read(my_dir + "/.wol_config.ini")
    sections = config.sections()

    for section in sections:
        options = config.options(section)

        sect_key = section
        my_config[sect_key] = {}

        for option in options:
            my_config[sect_key][option] = config.get(section, option)

    return my_config  # Useful for testing


def usage():
    print('Usage: wol.py [hostname]')


if __name__ == '__main__':
    my_dir = os.path.dirname(os.path.abspath(__file__))
    conf = load_config()
    try:
        # Use mac addresses with any separators.
        if sys.argv[1] == 'list':
            print('Configured Hosts:')
            for i in conf:
                if i != 'General':
                    print('\t', i)
            print('\n')
        else:
            if not wake_on_lan(sys.argv[1]):
                print('Invalid Hostname specified')
            else:
                print('Magic packet should be winging its way')
    except KeyError:
        usage()
