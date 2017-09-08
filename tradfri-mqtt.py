#!/usr/bin/env python

from tradfri.tradfri_daemon import Daemon
import sys, time, ConfigParser, os, json, signal
import paho.mqtt.client as mqtt
import tradfri.tradfri_get_json as js

client = mqtt.Client("Tradfri")
cfg = os.getcwd()+'/tradfri.cfg'
running = False

class MyDaemon(Daemon):
    # loop flag: True, loop running; False, loop stopped
    flag = True
    # signal handler for TERM and INT signals from main process
    def sigh(self, signum, frame):
       if signum in (signal.SIGTERM, signal.SIGINT):
                self.flag = False
    # runner that we override
    def run(self):
	global running
	global client
	# catch signals and call signal handler metdhod when caught
	signal.signal(signal.SIGTERM, self.sigh)
	signal.signal(signal.SIGINT, self.sigh)
	# setup everything and connect, subscribe etc
	mqtt_srv, mqtt_port, topic, hubip, securityid = setup()
	client.connect(mqtt_srv, mqtt_port, 60)
	(result, mid) = client.subscribe([(topic+"/devices/todo", 1), (topic+"/groups/todo", 1)])
	if result == mqtt.MQTT_ERR_SUCCESS:
	    pass
	else:
    	    sys.stderr.write(result+'\n')
	client.loop_start()
	time.sleep(0.2)
	# main loop that works in a forked process
	while self.flag == True:
	    # get group data as json and publish to /groups topic
	    msg = js.get_groups_json(hubip, securityid)
	    for _ in range(len(msg)):
		msg_json = json.loads(msg[_])
		id = str(msg_json["ID"])
		(result, mid) = client.publish(topic+"/groups"+id, str(msg_json), 1, False)
		if result == mqtt.MQTT_ERR_SUCCESS:
		    pass
		else:
    		    sys.stderr.write(result+'\n')
	    # get devices data as json and publis to /devices topic
	    msg = js.get_ldevs_json(hubip, securityid)
	    for _ in range(len(msg)):
		msg_json = json.loads(msg[_])
		id = str(msg_json["ID"])
		(result, mid) = client.publish(topic+"/devices"+id, str(msg_json), 1, False)
		if result == mqtt.MQTT_ERR_SUCCESS:
		    pass
		else:
    		    sys.stderr.write(result+'\n')
	    # we are running, wait for a while
	    running = True
    	    time.sleep(1)
	# we're not running anymore, unsubscribe and disconnect
	running = False
	client.unsubscribe([topic+"/devices/todo", topic+"/groups/todo"])
	time.sleep(0.5)
	client.disconnect()
	time.sleep(0.5)

def on_connect(client, userdata, flags, rc):
    sys.stderr.write("Connected with result code "+str(rc)+"\n")
    time.sleep(0.1)
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe(topic)

def on_disconnect(client, userdata, rc):
    if rc != mqtt.MQTT_ERR_SUCCESS:
        sys.stderr.write("Unexpected disconnection"+str(rc)+"\n")
    else:
	sys.stderr.write("Disconnected succesfully\n")
	client.loop_stop()
	time.sleep(0.2)

def on_message(client, userdata, msg):
    sys.stderr.write("message on: "+msg.topic+" : "+str(msg.payload)+"\n")
    # check message content
    try:
	m = json.loads(msg.payload)
	id = m["ID"]
	st = m["State"]
    except ValueError:
	pass
    # check current status st of device id and change accordingly

def on_publish(client, userdata, mid):
    sys.stderr.write("message sent: " + str(mid)+"\n")

def on_subscribe(client, userdata, mid, granted_qos):
    sys.stderr.write("Subscribed: " + str(mid) + " " + str(granted_qos)+"\n")
    
def on_unsubscribe(client, userdata, mid):
    sys.stderr.write("Unsubscribed: " + str(mid) + "\n")

def on_log(client, userdata, level, string):
    sys.stderr.write(string+"\n")

def setup():
    global client
    # read configuration from cfg file
    conf = ConfigParser.ConfigParser()
    conf.read(cfg)
    mqtt_srv = conf.get('tradfri', 'mqtt_srv')
    mqtt_port = conf.get('tradfri', 'mqtt_port')
    topic = conf.get('tradfri', 'topic')
    hubip = conf.get('tradfri', 'hubip')
    securityid = conf.get('tradfri', 'securityid')
    # define callback methods
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_unsubscribe = on_unsubscribe
    client.will_set = (topic, "Tradfri went offline!", 1, True)
    #client.on_log = on_log

    return mqtt_srv, mqtt_port, topic, hubip, securityid

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
