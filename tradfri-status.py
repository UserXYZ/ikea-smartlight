#!/usr/bin/env python

# file        : tradfri-status.py
# purpose     : getting status from the Ikea tradfri smart lights
#
# author      : harald van der laan
# date        : 2017/04/10
# version     : v1.1.0
#
# changelog   :
# - v1.1.0      refactor for cleaner code                               (harald)
# - v1.0.0      initial concept                                         (harald)
#
# - further modified by Floyd

"""
    tradfri-status.py - getting status of the Ikea Tradfri smart lights

    This module requires libcoap with dTLS compiled, at this moment there is no python coap module
    that supports coap with dTLS. see ../bin/README how to compile libcoap with dTLS support
"""

# pylint convention disablement:
# C0103 -> invalid-name
# C0200 -> consider-using-enumerate
# pylint: disable=C0200, C0103

# from __future__ import print_function

import sys
import time
import ConfigParser

from tradfri import tradfriStatus
from tradfri import tradfriAPI as API

def main():
    """ main function """
    conf = ConfigParser.ConfigParser()
    conf.read('tradfri.cfg')

    hubip = conf.get('tradfri', 'hubip')
    securityid = conf.get('tradfri', 'securityid')

    lightbulb = []
    lightgroup = []

    print('[ ] Tradfri: acquiring all Tradfri devices, please wait ...')
    devices = tradfriStatus.tradfri_get_devices(hubip, securityid)
    groups = tradfriStatus.tradfri_get_groups(hubip, securityid)

    for deviceid in (range(len(devices))):
        lightbulb.append(tradfriStatus.tradfri_get_lightbulb(hubip, securityid, str(devices[deviceid])))

    # sometimes the request are to fast, the hub will decline the request (flood security)
    # in this case you could increse the sleep timer
    time.sleep(.5)
    for groupid in (range(len(groups))):
        lightgroup.append(tradfriStatus.tradfri_get_group(hubip, securityid, str(groups[groupid])))

    print('[+] Tradfri: device information gathered')
    print('===========================================================\n')

    for _ in range(len(lightbulb)):
        try:
	    state = lightbulb[_][API._DEVICE_DATA_][0][API._ONOFF_]
            print('bulb ID {}, name: {}, brightness: {}, state: {}'
                      .format(lightbulb[_][API._ID_], lightbulb[_][API._NAME_], lightbulb[_][API._DEVICE_DATA_][0][API._DIMMER_], API._STATE_[state]))
        except KeyError:
            # device is not a lightbulb but a remote control, dimmer or sensor
            pass

    print('\n')

    for _ in range(len(lightgroup)):
	    gstate = lightgroup[_][API._ONOFF_]
            print('group ID: {}, name: {}, state: {}'
                  .format(lightgroup[_]["9003"], lightgroup[_]["9001"], API._STATE_[gstate]))

if __name__ == "__main__":
    main()
    sys.exit(0)
