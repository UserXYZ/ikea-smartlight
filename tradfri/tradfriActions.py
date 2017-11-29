#!/usr/bin/env python

# file        : tradfri/tradfriActions.py
# purpose     : module for controling status of the Ikea tradfri smart lights
#
# author      : harald van der laan
# date        : 2017/04/10
# version     : v1.1.0

import sys, os, json, subprocess
from shlex import split

# import directly from same package/folder
#sys.path.append(os.path.abspath(os.path.dirname(__file__)))

global coap
coap = '/usr/local/bin/coap-client'

def send(ident, psk, payload, tradfriHub, method='put'):

    api = '{} -m {} -u "{}" -k "{}" -e \'{}\' "{}"' .format(coap, method, ident, psk, payload, tradfriHub)
    
    try:
	p1 = subprocess.Popen(split(api), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=False)
    except OSError as err:
        print(str(err.strerror)+"[-] libcoap: could not find libcoap")
        return False
    try:
	p2 = subprocess.Popen(["/usr/bin/awk", "NR==2"], stdin=p1.stdout, stdout=subprocess.PIPE)
    except OSError as err:
        print(str(err.strerror)+"[-] awk: could not find awk")
        return False
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    result = p2.communicate()[0]

    return result

def tradfri_power_light(hubip, ident, psk, lightbulbid, value):
    """ function for powering on/off single tradfri lightbulb """
    tradfriHub = 'coaps://{}:5684/15001/{}' .format(hubip, lightbulbid)

    if value == 'On':
        payload = '{ "3311": [{ "5850": 1 }] }'
    elif value == 'Off':
        payload = '{ "3311": [{ "5850": 0 }] }'
    else:
	return False

    return send(ident, psk, payload, tradfriHub)

def tradfri_dim_light(hubip, ident, psk, lightbulbid, value):
    """ function for dimming single tradfri lightbulb """
    dim = float(value) * 2.55
    tradfriHub = 'coaps://{}:5684/15001/{}'.format(hubip, lightbulbid)
    payload = '{ "3311" : [{ "5851" : %s }] }' % int(dim)

    return send(ident, psk, payload, tradfriHub)

def tradfri_color_light(hubip, ident, psk, lightbulbid, value):
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

    return send(ident, psk, payload, tradfriHub)

def tradfri_power_group(hubip, ident, psk, groupid, value):
    """ function for powering on/off tradfri lightbulb group """
    tradfriHub = 'coaps://{}:5684/15004/{}' .format(hubip, groupid)

    if value == 'On':
        payload = '{ "5850" : 1 }'
    elif value == 'Off':
        payload = '{ "5850" : 0 }'
    else:
	return False

    return send(ident, psk, payload, tradfriHub)

def tradfri_dim_group(hubip, ident, psk, groupid, value):
    """ function for dimming tradfri lightbulb group """
    tradfriHub = 'coaps://{}:5684/15004/{}'.format(hubip, groupid)
    dim = float(value) * 2.55
    payload = '{ "5851" : %s }' % int(dim)

    return send(ident, psk, payload, tradfriHub)

def get_psk(hubip, securityid, ident):
###coap-client -m post -u 'Client_identity' -k 'SECURITY_CODE' -e '{"9090":"IDENTITY"}' 'coaps://IP_ADDRESS:5684/15011/9063'
###coap-client -m get -u "IDENTITY" -k "PRE_SHARED_KEY" "coaps://IP_ADDRESS:5684/15001"
    """ function for getting preshared key from securityid """
    tradfriHub = 'coaps://{}:5684/15011/9063' .format(hubip)
    payload = '{ "9090": "%s" }' % ident
    r = send("Client_identity", securityid, payload, tradfriHub, 'post')
    try:
	result = json.loads(r.strip('\n'))
	return result["9091"]
    except TypeError:
	return False

