#!/usr/bin/env python

# file        : tradfri/tradfriActions.py
# purpose     : module for controling status of the Ikea tradfri smart lights
#
# author      : harald van der laan
# date        : 2017/04/10
# version     : v1.1.0
#
# changelog   :
# - v1.1.0      refactor for cleaner code                               (harald)
# - v1.0.0      initial concept                                         (harald)

"""
    tradfri/tradfriActions.py - controlling the Ikea tradfri smart lights

    This module requires libcoap with dTLS compiled, at this moment there is no python coap module
    that supports coap with dTLS. see ../bin/README how to compile libcoap with dTLS support
"""

# pylint convention disablement:
# C0103 -> invalid-name
# pylint: disable=C0103

import sys, os, subprocess
from shlex import split
from tradfri.tradfriHelper import errmsg as errmsg

global coap
coap = '/usr/local/bin/coap-client'

def send(cmd):
    try:
	return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)
    except subprocess.CalledProcessError as err:
        errmsg("Bad arguments for libcoap: "+str(err.output))
    except OSError as err:
        errmsg(str(err.strerror)+"[-] libcoap: could not find libcoap")

    return False

def tradfri_power_light(hubip, securityid, lightbulbid, value):
    """ function for powering on/off single tradfri lightbulb """
    tradfriHub = 'coaps://{}:5684/15001/{}' .format(hubip, lightbulbid)

    if value == 'On':
        payload = '{ "3311": [{ "5850": 1 }] }'
    elif value == 'Off':
        payload = '{ "3311": [{ "5850": 0 }] }'
    else:
	return False

    cmd = '{} -m put -u "Client_identity" -k "{}" -e \'{}\' "{}"' .format(coap, securityid, payload, tradfriHub)
    return send(split(cmd))

def tradfri_dim_light(hubip, securityid, lightbulbid, value):
    """ function for dimming single tradfri lightbulb """
    dim = float(value) * 2.55
    tradfriHub = 'coaps://{}:5684/15001/{}'.format(hubip, lightbulbid)
    payload = '{ "3311" : [{ "5851" : %s }] }' % int(dim)

    cmd = '{} -m put -u "Client_identity" -k "{}" -e \'{}\' "{}"'.format(coap, securityid, payload, tradfriHub)
    return send(split(cmd))

def tradfri_color_light(hubip, securityid, lightbulbid, value):
    """ function for setting color temperature for single tradfri lightbulb """
    tradfriHub = 'coaps://{}:5684/15001/{}'.format(hubip, lightbulbid)

    if value == 'Warm':
        payload = '{ "3311" : [{ "5709" : %s, "5710": %s }] }' % ("33135", "27211")
    elif value == 'Normal':
        payload = '{ "3311" : [{ "5709" : %s, "5710": %s }] }' % ("30140", "26909")
    elif value == 'Cold':
        payload = '{ "3311" : [{ "5709" : %s, "5710": %s }] }' % ("24930", "24684")
    else:
	return False

    cmd = '{} -m put -u "Client_identity" -k "{}" -e \'{}\' "{}"'.format(coap, securityid, payload, tradfriHub)
    return send(split(cmd))

def tradfri_power_group(hubip, securityid, groupid, value):
    """ function for powering on/off tradfri lightbulb group """
    tradfriHub = 'coaps://{}:5684/15004/{}' .format(hubip, groupid)

    if value == 'On':
        payload = '{ "5850" : 1 }'
    elif value == 'Off':
        payload = '{ "5850" : 0 }'
    else:
	return False

    cmd = '{} -m put -u "Client_identity" -k "{}" -e \'{}\' "{}"' .format(coap, securityid, payload, tradfriHub)
    return send(split(cmd))

def tradfri_dim_group(hubip, securityid, groupid, value):
    """ function for dimming tradfri lightbulb group """
    tradfriHub = 'coaps://{}:5684/15004/{}'.format(hubip, groupid)
    dim = float(value) * 2.55
    payload = '{ "5851" : %s }' % int(dim)

    cmd = '{} -m put -u "Client_identity" -k "{}" -e \'{}\' "{}"'.format(coap, securityid, payload, tradfriHub)
    return send(cmd)
