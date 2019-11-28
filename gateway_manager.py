#!/usr/bin/python3
#
# This demo script use Linux NETLINK IPC to monitor
# and manage default network gateway.
#
# It reads REDIS for preferred network interface device
# and IPv4 address. Whenever that device comes online 
# with that IPv4 address, it changes the default network 
# gateway to that device.
#
# A typical use case of this script is mobility management
# of MPTCP enabled UE in 5G service based architecture (SBA).
# The script switches to fastest network connection 
# (configureable via REDIS backend service) as soon as it 
# becomes available without breaking any active communication 
# session.
#
# Copyright (c) 2018, 2019, Burraq Technologies UG
#
import redis
from socket import AF_INET
from pyroute2 import IPRoute
from pprint import pprint

# debug settings
debug = 0

# redis settings
redis_host = 'localhost'
redis_port = 6379
redis_db   = 0

# default settings - used when redis is unavailable
default_inet = 'wlx801f02cd4b98'
default_ipv4 = '192.168.8.140'

######################################################################

def get_preferences():
    r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    ret = dict()

    preferred_inet = r.get('GET pref-inet')
    if not preferred_inet:
        preferred_inet = default_inet
    print("Preferred Interface:", preferred_inet)
    ret['inet'] = preferred_inet
    
    preferred_ipv4 = r.get('GET pref-ipv4')
    if not preferred_ipv4:
        preferred_ipv4 = default_ipv4
    print("Preferred IPv4:", preferred_ipv4)
    ret['ipv4'] = preferred_ipv4

    with IPRoute() as ipr:
        for x in ipr.get_routes(table=254):
            dev = ipr.link_lookup(ifname=preferred_inet)
            if (dev and x.get_attr('RTA_OIF') == dev[0]):
                route = dict()
                route['dev']  = x.get_attr('RTA_OIF')
                route['gw']   = x.get_attr('RTA_GATEWAY')
                route['prio'] = x.get_attr('RTA_PRIORITY')
                print("Preferred Route:", route, "\n")
                ret['route'] = route
                break

        check = False
        for x in ipr.get_addr(family=AF_INET, label=preferred_inet):
            if x.get_attr('IFA_ADDRESS') == preferred_ipv4:
                check = True
                break

        if (check):
            if debug:
                print("Set preferences:", preferred_ipv4, "assigned to", 
                        preferred_inet, "and route", route, "\n")
        else:
            if debug:
                print("Bad preferences:", preferred_ipv4, 
                        "is not assigned to", preferred_inet)

    return ret


prefs = get_preferences()
print("Current Network Status:", prefs, "\n")

# With IPRoute objects you have to call bind() manually
with IPRoute() as ipr:
    ipr.bind()
    while 1:
        for message in ipr.get():
            # print all messages - for debugging only
            #pprint(message)

            # process only new IPv4 address events
            if (message.get('event') == 'RTM_NEWADDR' and 
                    message.get('family') == AF_INET):
                # print all new ip messages - for debugging only
                #pprint(message)
                #print("\n")

                prefs = get_preferences()
                if (prefs['route']['dev'] == message.get('index') and 
                        prefs['route']['gw']):
                    if debug:
                        pprint(message)
                        print("\n")

                    print("Changing default gateway to", 
                            prefs['route']['gw'])

                    # delete default gateway if exists
                    ipr.route("del", dst="default")

                    # add new default gateway
                    ipr.route("add", dst="default", 
                            gateway=prefs['route']['gw'])


