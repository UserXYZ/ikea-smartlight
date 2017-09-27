#!/usr/bin/env python

from tradfri.tradfri_daemon import Daemon
import sys, time, ConfigParser, os, json, signal
import paho.mqtt.client as mqtt
import tradfri.tradfri_get_json as js
import tradfri.tradfriActions as act
from tradfri.tradfriHelper import errmsg as errmsg

client = mqtt.Client("Tradfri")
cfg = os.getcwd()+'/tradfri.cfg'
running = False
devids = set()
groupids = set()

class MyDaemon(Daemon):
    # loop flag: True, loop running; False, loop stopped
    flag = True
    # signal handler for TERM and INT signals from main process
    def sigh(self, signum, frame):
       if signum in (signal.SIGTERM, signal.SIGINT):
                self.flag = False
    # runner that we override
    def run(self):
	global running, client, devids, groupids
	
	# catch signals and call signal handler metdhod when caught
	signal.signal(signal.SIGTERM, self.sigh)
	signal.signal(signal.SIGINT, self.sigh)
	# setup everything and connect, subscribe etc
	mqtt_srv, mqtt_port, topic, hubip, securityid = get_config()
	setup()
	client.connect(mqtt_srv, mqtt_port, 60)
	(result, mid) = client.subscribe([(topic+"/devices/todo", 1), (topic+"/groups/todo", 1)])
	if result == mqtt.MQTT_ERR_SUCCESS:
	    pass
	else:
    	    errmsg(result)
	client.loop_start()
	time.sleep(0.2)
	# main loop that works in a forked process
	while self.flag == True:
	    # clean device and group id lists
	    #devids.clear()
	    #groupids.clear()
	    # get group data as json and publish to /groups topic
	    msg = js.get_groups_json(hubip, securityid)
	    for _ in range(len(msg)):
		msg_json = json.loads(msg[_])
		id = msg_json["ID"]
		if id: # got something, append to device id list
		    groupids.add(id)
		(result, mid) = client.publish(topic+"/groups", msg[_], 1, False)
		if result == mqtt.MQTT_ERR_SUCCESS:
		    pass
		else:
    		    errmsg(result)
    	    time.sleep(1)
	    # get devices data as json and publis to /devices topic
	    msg = js.get_ldevs_json(hubip, securityid)
	    for _ in range(len(msg)):
		msg_json = json.loads(msg[_])
		id = msg_json["ID"]
		if id: # got something, append to group id list
		    devids.add(id)
		(result, mid) = client.publish(topic+"/devices", msg[_], 1, False)
		if result == mqtt.MQTT_ERR_SUCCESS:
		    pass
		else:
    		    errmsg(result)
	    # we are running, wait for a while
	    running = True
    	    time.sleep(4)
	# we're not running anymore, unsubscribe and disconnect
	running = False
	client.unsubscribe([topic+"/devices/todo", topic+"/groups/todo"])
	time.sleep(0.5)
	client.disconnect()
	time.sleep(0.5)

def on_connect(client, userdata, flags, rc):
    errmsg("Connected with result code "+str(rc))
    time.sleep(0.5)
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe(topic)

def on_disconnect(client, userdata, rc):
    if rc != mqtt.MQTT_ERR_SUCCESS:
        errmsg("Unexpected disconnection"+str(rc))
    else:
	errmsg("Disconnected succesfully")
	client.loop_stop()
	time.sleep(0.5)

def on_message(client, userdata, msg):
    global devids, groupids

    mqtt_srv, mqtt_port, topic, hubip, securityid = get_config()

    errmsg("message on: "+msg.topic+" : "+str(msg.payload))
    # check message content
    try:
	m = json.loads(msg.payload)
	id = m["ID"]
	sid = str(id)
	# parse message by ID
	# first, check if ID exists
	#errmsg("got id: "+sid)
	if id > 65535:
	    text=""
	    if "State" in m:
		st = m["State"]
		text=text+" State: "+st+" "
	    else:
		st = None
	    if "Brightness" in m:
		brt = m["Brightness"]
		text=text+" Brightness: "+str(brt)+" "
	    else:
		brt = None
	    if "Color" in m:
		col = m["Color"]
		text=text+" Color: "+str(col)+" "
	    else:
		col = None
	    #errmsg("got id: "+sid+" "+text)
	    #errmsg(str(devids))
	    # then check what id it is of
	    if sid in devids: # normal lights
	        errmsg("id "+sid+" is in device list")
	    	if st:
	    	    res = act.tradfri_power_light(hubip, securityid, id, st)
	    	    if res != False:
	    	        pass
		    else:
		        errmsg("Bad result from COAP client")
		if brt:
		    res = act.tradfri_dim_light(hubip, securityid, id, brt)
		    if res:
	    	        pass
		    else:
		        errmsg("Bad result from COAP client")
		if col:
		    res = act.tradfri_color_light(hubip, securityid, id, col)
		    if res != False:
			pass
		    else:
			errmsg("Bad color code, can be only 'Warm', 'Normal', or 'Cold'")
	        # send command to device
	    elif sid in groupids: # light groups
	        errmsg("id "+sid+" is in group list")
	        if st:
	    	    res = act.tradfri_power_group(hubip, securityid, id, st)
	    	    if res != False:
	    		pass
		    else:
			errmsg("Bad result from COAP client")
		if brt:
		    res = act.tradfri_dim_group(hubip, securityid, id, brt)
		    if res:
	    	        pass
		    else:
		        errmsg("Bad result from COAP client")
	        # send command to group
	    else:
	        errmsg("id "+sid+" is not in device or group id lists")
	        pass
	else:
	    errmsg("ID wrong")
    except (TypeError, ValueError) as err:
	errmsg(str(err))
    except KeyError as err:
	errmsg("Value missing from JSON: "+str(err))

def on_publish(client, userdata, mid):
    errmsg("message sent: " + str(mid))

def on_subscribe(client, userdata, mid, granted_qos):
    errmsg("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_unsubscribe(client, userdata, mid):
    errmsg("Unsubscribed: " + str(mid))

def on_log(client, userdata, level, string):
    errmsg(string+"\n")

def get_config():
    # read configuration from cfg file
    conf = ConfigParser.ConfigParser()
    conf.read(cfg)
    mqtt_srv = conf.get('tradfri', 'mqtt_srv')
    mqtt_port = conf.get('tradfri', 'mqtt_port')
    topic = conf.get('tradfri', 'topic')
    hubip = conf.get('tradfri', 'hubip')
    securityid = conf.get('tradfri', 'securityid')
    return mqtt_srv, mqtt_port, topic, hubip, securityid

def setup():
    global client

    mqtt_srv, mqtt_port, topic, hubip, securityid = get_config()
    # define callback methods
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_unsubscribe = on_unsubscribe
    client.will_set = (topic, "Tradfri went offline!", 1, True)
    #client.on_log = on_log

def main():
    # create new daemon
    daemon = MyDaemon('/tmp/tradfri-daemon.pid', '/dev/null', '/dev/null', '/dev/stderr')
    if len(sys.argv) == 2:
	if 'start' == sys.argv[1]:
	    print "starting\n"
    	    daemon.start()
        elif 'stop' == sys.argv[1]:
    	    print "stopping\n"
    	    daemon.stop()
	    if running == True:
		print "still running\n"
	    else:
		print "not running\n"
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
            sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)

if __name__ == "__main__":
    main()
    sys.exit(0)
