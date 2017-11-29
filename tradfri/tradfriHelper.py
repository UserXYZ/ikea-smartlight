#!/usr/bin/env python

import os, sys, time, ConfigParser
from .tradfriActions import get_psk as get_psk

def errmsg(err):
    if err:
	t=time.strftime("%c",time.localtime())+" : "
	sys.stderr.write(t+err+"\n")

def make_cfg(cfg, hubip, securityid):
    conf=ConfigParser.ConfigParser()
    if conf.read(cfg):
	import uuid
	ident = uuid.uuid4()
	conf.set('tradfri','ident', ident)
	psk = get_psk(hubip, securityid, ident)
	if psk == False:
	    errmsg("Can't get PSK!")
	    return False
	else:
	    conf.set('tradfri','psk', psk)
	    try:
	        file = open(cfg, 'w')
		conf.write(file)
		file.close()
	    except IOError:
    	        errmsg("Can't open config file for writing!"), arg
    	        return False
	return True
    else:
	errmsg("No config file!")
	return False
