#!/usr/bin/env python

import sys, time

def errmsg(err):
    if err:
	t=time.strftime("%c",time.localtime())+" : "
	sys.stderr.write(t+err+"\n")
