# gateway-manager
A demo script to switch to fastest pre-configured network gateway 
as soon as it becomes available

## description
This demo script use Linux NETLINK IPC to monitor and manage 
default network gateway.

It reads REDIS for preferred network interface device and IPv4 
address. Whenever that device comes online with that IPv4 address, 
it changes the default network gateway to that device.

A typical use case of this script is mobility management of MPTCP 
enabled UE in 5G service based architecture (SBA). The script 
switches to fastest network connection (configurable via REDIS 
back-end service) as soon as it becomes available without breaking 
any active communication session.

### Dependencies
* Python version 2.x or 3.x (Python 3.x recommended)
* Linux NETLINK IPC library for Python 
(`python-pyroute2` or `python3-pyroute2`)
* REDIS Library 
(`python-hiredis` or `python3-hiredis`)
* MPTCP enabled Linux kernel (optional)

### Usage
* In REDIS server, set keys `pref-inet` and `pref-ipv4` appropriate 
values for network interfaceand its IPv4 address respectively.
* Edit script to set appropriate redis connection parameters, by
default it uses host `localhost` and port `6379`.
* Simply run the script `$(pwd)/home/shahzad/shari/gateway-manager`

Sample output

```
Preferred Interface: wlx801f02cd4b98
Preferred IPv4: 192.168.8.140
Preferred Route: {'dev': 13, 'gw': '192.168.8.1', 'prio': 601} 

Changing default gateway to 192.168.8.1
```

#### Copyright
Copyright (c) 2019 Muhammad Shahzad Shafi <mshahzad@burraq-technologies.de>

