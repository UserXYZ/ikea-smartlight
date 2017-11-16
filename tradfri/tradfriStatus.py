#!/usr/bin/env python

# file        : tradfri/tradfriStatus.py
# purpose     : getting status from the Ikea tradfri smart lights
#
# author      : harald van der laan
# date        : 2017/04/10
# version     : v1.1.0
#

import sys, os, json, subprocess
from shlex import split

from .tradfriHelper import errmsg as errmsg

global coap
coap = '/usr/local/bin/coap-client'
###coap-client  -m get  -u "Confuzed22" -k "6V6TYU3VlkR13TWp" "coaps://10.20.30.25:5684/15001/65537" 2>/dev/stdout|awk 'NR==2'

def send(ident, psk, payload, tradfriHub):
    api = '{} -m put -u "{}" -k "{}" -e \'{}\' "{}"' .format(coap, ident, psk, payload, tradfriHub)

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

def tradfri_get_devices(hubip, ident, psk):
    """ function for getting all tradfri device ids """
    tradfriHub = 'coaps://{}:5684/15001' .format(hubip)

    result = send(ident, psk, tradfriHub)

    try:
	return json.loads(result.strip('\n'))
    except ValueError:
	errmsg("status-get_devices: Can't get devices")
	return False

def tradfri_get_lightdev(hubip, ident, psk, deviceid):
    """ function for getting tradfri lightbulb information """
    tradfriHub = 'coaps://{}:5684/15001/{}' .format(hubip, deviceid)

    result = send(ident, psk, tradfriHub)

    try:
	return json.loads(result.strip('\n'))
    except ValueError:
	errmsg("status-get_lightdev: Can't get device data")
	errmsg(str(result))
	return False

def tradfri_get_groups(hubip, ident, psk):
    """ function for getting tradfri groups """
    tradfriHub = 'coaps://{}:5684/15004'.format(hubip)

    result = send(ident, psk, tradfriHub)

    try:
	return json.loads(result.strip('\n'))
    except ValueError:
	errmsg("status-get_groups: Can't get groups")
	return False

def tradfri_get_group(hubip, ident, psk, groupid):
    """ function for getting tradfri group information """
    tradfriHub = 'coaps://{}:5684/15004/{}'.format(hubip, groupid)

    result = send(ident, psk, tradfriHub)

    try:
	return json.loads(result.strip('\n'))
    except ValueError:
	errmsg("status-get_group: Can't read group data")
	return False

def main():
    ConfigParser = __import__("ConfigParser")
    time = __import__("time")
    cfg = os.path.abspath(os.path.dirname(__file__))+'/../tradfri.cfg'
    conf = ConfigParser.ConfigParser()
    conf.read(cfg)
    mqtt_srv = conf.get('tradfri', 'mqtt_srv')
    mqtt_port = conf.get('tradfri', 'mqtt_port')
    topic = conf.get('tradfri', 'topic')
    hubip = conf.get('tradfri', 'hubip')
    securityid = conf.get('tradfri', 'securityid')
    psk = conf.get('tradfri', 'psk')
    ident = conf.get('tradfri', 'ident')

    print time.asctime()
    while True:
	""" works ok
	res = tradfri_get_devices(hubip, ident, psk)
	if res == False:
	    print time.asctime(), "Devices Faaaaail!"
	else:
	    print res
	time.sleep(2)
	res = tradfri_get_groups(hubip, ident, psk)
	if res == False:
	    print time.asctime(), "Groups Faaaaail!"
	else:
	    print res
	"""
	res = tradfri_get_lightdev(hubip, ident, psk, 65537)
	if res == False:
	    print time.asctime(), "get_lightdev Faaaaail!"
	else:
	    print time.clock(), res
	time.sleep(2)
	
if __name__ == "__main__":
    main()
    sys.exit(0)
