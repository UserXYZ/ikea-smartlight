#!/usr/bin/env python

# file        : tradfri/tradfriStatus.py
# purpose     : getting status from the Ikea tradfri smart lights
#
# author      : harald van der laan
# date        : 2017/04/10
# version     : v1.1.0
#
# changelog   :
# - v1.1.0      refactor for cleaner code                               (harald)
# - v1.0.0      initial concept                                         (harald)

"""
    tradfriStatus.py - module for getting status of the Ikea tradfri smart lights

    This module requires libcoap with dTLS compiled, at this moment there is no python coap module
    that supports coap with dTLS. see ../bin/README how to compile libcoap with dTLS support
"""

# pylint convention disablement:
# C0103 -> invalid-name
# pylint: disable=C0103

import sys, os, json, subprocess
from shlex import split
# import directly from same package/folder
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from tradfriHelper import errmsg as errmsg

global coap
coap = '/usr/local/bin/coap-client.old'

def send(api):
    try:
	p1 = subprocess.Popen(split(api), stdout=subprocess.PIPE, universal_newlines=True, shell=False)
    except OSError as err:
        print(str(err.strerror)+"[-] libcoap: could not find libcoap")
        return False
    try:
	p2 = subprocess.Popen(["/usr/bin/awk", "NR==5"], stdin=p1.stdout, stdout=subprocess.PIPE)
    except OSError as err:
        print(str(err.strerror)+"[-] awk: could not find awk")
        return False
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    result = p2.communicate()[0]
    
    return result

def tradfri_get_devices(hubip, securityid):
    """ function for getting all tradfri device ids """
    tradfriHub = 'coaps://{}:5684/15001' .format(hubip)
    #api = '{} -m get -u "Client_identity" -k "{}" "{}" | awk \'NR==4\''.format(coap, securityid, tradfriHub)
    api = '{} -m get -u "Client_identity" -k "{}" "{}"'.format(coap, securityid, tradfriHub)

    result = send(api)

    try:
	return json.loads(result.strip('\n'))
    except ValueError:
	errmsg("status-get_devices: Can't get devices")
	return False

def tradfri_get_lightdev(hubip, securityid, deviceid):
    """ function for getting tradfri lightbulb information """
    tradfriHub = 'coaps://{}:5684/15001/{}' .format(hubip, deviceid)
    #api = '{} -m get -u "Client_identity" -k "{}" "{}" | awk \'NR==4\''.format(coap, securityid, tradfriHub)
    api = '{} -m get -u "Client_identity" -k "{}" "{}"'.format(coap, securityid, tradfriHub)

    result = send(api)

    try:
	return json.loads(result.strip('\n'))
    except ValueError:
	errmsg("status-get_lightdev: Can't get device data")
	errmsg(str(result))
	return False

def tradfri_get_groups(hubip, securityid):
    """ function for getting tradfri groups """
    tradfriHub = 'coaps://{}:5684/15004'.format(hubip)
    #api = '{} -m get -u "Client_identity" -k "{}" "{}" | awk \'NR==4\''.format(coap, securityid, tradfriHub)
    api = '{} -m get -u "Client_identity" -k "{}" "{}"'.format(coap, securityid, tradfriHub)

    result = send(api)

    try:
	return json.loads(result.strip('\n'))
    except ValueError:
	errmsg("status-get_groups: Can't get groups")
	return False

def tradfri_get_group(hubip, securityid, groupid):
    """ function for getting tradfri group information """
    tradfriHub = 'coaps://{}:5684/15004/{}'.format(hubip, groupid)
    #api = '{} -m get -u "Client_identity" -k "{}" "{}" | awk \'NR==4\''.format(coap, securityid, tradfriHub)
    api = '{} -m get -u "Client_identity" -k "{}" "{}"'.format(coap, securityid, tradfriHub)

    result = send(api)

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

    print time.asctime()
    while True:
	""" works ok
	res = tradfri_get_devices(hubip, securityid)
	if res == False:
	    print time.asctime(), "Devices Faaaaail!"
	else:
	    print res
	time.sleep(2)
	res = tradfri_get_groups(hubip, securityid)
	if res == False:
	    print time.asctime(), "Groups Faaaaail!"
	else:
	    print res
	"""
	res = tradfri_get_lightdev(hubip, securityid, 65537)
	if res == False:
	    print time.asctime(), "get_lightdev Faaaaail!"
	else:
	    print time.clock(), res
	time.sleep(2)
	
if __name__ == "__main__":
    main()
    sys.exit(0)
