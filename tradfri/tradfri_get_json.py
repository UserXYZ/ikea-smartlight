#!/usr/bin/env python

import sys
import json

from tradfri import tradfriStatus
from tradfri import tradfriAPI as API

gldevs = []

def get_ldevs(hubip, securityid):
    lightdev = []
    ldevs = []
    devices = tradfriStatus.tradfri_get_devices(hubip, securityid)
    #sys.stderr.write(str(devices)+"\n")
    try:
	for deviceid in (range(len(devices))):
    	    lightdev.append(tradfriStatus.tradfri_get_lightdev(hubip, securityid, str(devices[deviceid])))
    except TypeError:
	sys.stderr.write("Can't get devices\n")
	return ldevs
    #sys.stderr.write(str(lightdev)+"\n")
    for _ in range(len(lightdev)):
        try:
	    devs = []
	    st = lightdev[_][API._DEVICE_DATA_][0][API._ONOFF_]
	    devtype = lightdev[_]["3"]["1"]
	    brightness = int(round(lightdev[_][API._DEVICE_DATA_][0][API._DIMMER_]/2.54))
	    id = lightdev[_][API._ID_]
	    devname = lightdev[_][API._NAME_]
	    state = API._STATE_[st]
	    gldevs.append(id)
	    devs = [id, devtype, devname, state, brightness]
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
    		"Brightness":ldevs[_][4]}))
    return ldevs_json

def get_groups_json(hubip, securityid):
    groups_json = []
    lightgroup = []
    groups = tradfriStatus.tradfri_get_groups(hubip, securityid)
    ldevs = get_ldevs(hubip, securityid)

    try:
	for groupid in (range(len(groups))):
    	    lightgroup.append(tradfriStatus.tradfri_get_group(hubip, securityid, str(groups[groupid])))
    except TypeError:
	sys.stderr.write("Can't get groups\n")
	return groups_json

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
    return groups_json
