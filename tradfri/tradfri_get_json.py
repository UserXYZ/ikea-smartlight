#!/usr/bin/env python

import sys, json, os
from time import sleep
import .tradfriStatus
import .tradfriAPI as API
from .tradfriHelper import errmsg as errmsg

gldevs = []

def get_ldevs(hubip, securityid):
    lightdev = []
    ldevs = []
    devices = tradfriStatus.tradfri_get_devices(hubip, securityid)
    if devices is False:
	errmsg("json-get_ldevs: can't get devices")
	return ldevs
    #errmsg(str(devices))
    if len(devices) > 0:
	try:
	    for deviceid in (range(len(devices))):
		#lightdev.append(tradfriStatus.tradfri_get_lightdev(hubip, securityid, str(devices[deviceid])))
		ldev = tradfriStatus.tradfri_get_lightdev(hubip, securityid, str(devices[deviceid]))
		if ldev is not False:
    		    lightdev.append(ldev)
	except TypeError:
	    errmsg("Can't get devices")
	    return ldevs
    else:
	errmsg("json-get_ldevs: can't read devices")
	return ldevs
    #errmsg(str(lightdev)+"\n")
    for _ in range(len(lightdev)):
        try:
	    devs = []
	    st = lightdev[_][API._DEVICE_DATA_][0][API._ONOFF_]
	    devtype = lightdev[_]["3"]["1"]
	    brightness = int(round(lightdev[_][API._DEVICE_DATA_][0][API._DIMMER_]/2.54))
	    color = str(lightdev[_][API._DEVICE_DATA_][0][API._COL_])
	    id = lightdev[_][API._ID_]
	    devname = lightdev[_][API._NAME_]
	    state = API._STATE_[st]
	    gldevs.append(id)
	    devs = [id, devtype, devname, state, brightness, color]
	    ldevs.append(devs)
        except KeyError:
            # device is not a lightbulb but a remote control, dimmer or sensor
            pass
    return ldevs

def get_ldevs_json(hubip, securityid):
    ldevs_json = []
    ldevs = get_ldevs(hubip, securityid)
    if len(ldevs) > 0: # something read from hub, exception didn't return an empty list
	for _ in range(len(ldevs)):
	    
	    ldevs_json.append(json.dumps({"ID":ldevs[_][0],
    		"DeviceType":ldevs[_][1],"DeviceName":ldevs[_][2],
    		"State":ldevs[_][3],
    		"Brightness":ldevs[_][4],
    		"Color":ldevs[_][5]
    		}))
    else:
	errmsg("json-get_ldevs_json: can't get ldevs")
    return ldevs_json

def get_groups_json(hubip, securityid):
    groups_json = []
    lightgroup = []
    groups = tradfriStatus.tradfri_get_groups(hubip, securityid)
    sleep(0.5) # give it some time
    ldevs = get_ldevs(hubip, securityid)

    if len(ldevs) == 0: # failed to read ldevs, bail out
	errmsg("json-get_groups_json: can't read ldevs")
	return groups_json
	
    if len(groups) > 0: # failed to read groups, bail out
	try:
	    for groupid in (range(len(groups))):
    		lightgroup.append(tradfriStatus.tradfri_get_group(hubip, securityid, str(groups[groupid])))
	except TypeError:
	    errmsg("json-get_groups_json: Can't get groups")
	    return groups_json
    else:
	errmsg("json-get_groups_json: can't get groups_json")
        return groups_json

    if len(lightgroup) > 0:
	for _ in range(len(lightgroup)):
	    ggdev = []
	    gdevs = lightgroup[_][API._HS_ACCESSORY_LINK_][API._HS_LINK_][API._ID_]
	    gstate = lightgroup[_][API._ONOFF_]
	    gbrightness = int(round(lightgroup[_][API._DIMMER_]/2.54))

	    for g in gdevs:
		for l in range(len(ldevs)):
			if(g == ldevs[l][0]):
			    ggdev.append(g)
	    
	    groups_json.append(json.dumps({"ID":lightgroup[_][API._ID_],
		"GroupName":lightgroup[_][API._NAME_],
		"State":API._STATE_[gstate],
		"Brightness":gbrightness,
		"Devices":ggdev}))
    else:
	errmsg("json-get_groups_json: can't get lightgroup")

    return groups_json


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
	res = get_ldevs(hubip, securityid)
	if res == False:
	    print time.asctime(), "get_ldevs Faaaaail!"
	else:
	    print time.clock(), res
	time.sleep(2)
	
if __name__ == "__main__":
    main()
    sys.exit(0)
