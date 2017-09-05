#!/usr/bin/env python

from tradfri.tradfri_daemon import Daemon
import sys, time, ConfigParser, os, json, signal
import paho.mqtt.client as mqtt
import tradfri.tradfri_get_json as js

client = mqtt.Client("Tradfri")
cfg = os.getcwd()+'/tradfri.cfg'
running = False

class MyDaemon(Daemon):
    flag = True

    def sigh(self, signum, frame):
       if signum in (signal.SIGTERM, signal.SIGINT):
                self.flag = False

    def run(self):
	global running
	global client

	signal.signal(signal.SIGTERM, self.sigh)
	signal.signal(signal.SIGINT, self.sigh)

	mqtt_srv, mqtt_port, topic, hubip, securityid = setup()
	client.connect(mqtt_srv, mqtt_port, 60)
	client.subscribe(topic)
	client.loop_start()
	
	while self.flag == True:
	    msg = js.get_groups_json(hubip, securityid)
	    for _ in range(len(msg)):
		msg_json = json.loads(msg[_])
		id = str(msg_json["ID"])
		(result, mid) = client.publish(topic+"/groups/"+id, str(msg_json), 1, True)
		if result == mqtt.MQTT_ERR_SUCCESS:
		    pass
		else:
    		    sys.stderr.write(result+'\n')
    		    sys.stderr.flush()

	    msg = js.get_ldevs_json(hubip, securityid)
	    for _ in range(len(msg)):
		msg_json = json.loads(msg[_])
		id = str(msg_json["ID"])
		(result, mid) = client.publish(topic+"/devices/"+id, str(msg_json), 1, True)
		if result == mqtt.MQTT_ERR_SUCCESS:
		    pass
		else:
    		    sys.stderr.write(result+'\n')
    		    sys.stderr.flush()

	    running = True
    	    time.sleep(1)

	running = False
	client.unsubscribe(topic)
	time.sleep(1)
	client.disconnect()
	time.sleep(1)

def on_connect(client, obj, flags, rc):
    sys.stderr.write("Connected with result code "+str(rc)+"\n")
    sys.stderr.flush()
    time.sleep(0.1)
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe(topic)

def on_disconnect(client, obj, rc):
    if rc != mqtt.MQTT_ERR_SUCCESS:
        sys.stderr.write("Unexpected disconnection"+str(rc)+"\n")
    else:
	sys.stderr.write("Disconnected succesfully\n")
	client.loop_stop()
	time.sleep(0.1)
    sys.stderr.flush()

def on_message(client, obj, msg):
    sys.stderr.write("message: "+msg.topic+" "+str(msg.payload)+"\n")
    sys.stderr.flush()

def on_publish(client, obj, mid):
    sys.stderr.write("message sent: " + str(mid)+"\n")
    sys.stderr.flush()

def on_subscribe(client, obj, mid, granted_qos):
    sys.stderr.write("Subscribed: " + str(mid) + " " + str(granted_qos)+"\n")
    sys.stderr.flush()

def on_log(client, obj, level, string):
    sys.stderr.write(string+"\n")
    sys.stderr.flush()

def setup():
    global client

    conf = ConfigParser.ConfigParser()
    conf.read(cfg)
    mqtt_srv = conf.get('tradfri', 'mqtt_srv')
    mqtt_port = conf.get('tradfri', 'mqtt_port')
    topic = conf.get('tradfri', 'topic')
    hubip = conf.get('tradfri', 'hubip')
    securityid = conf.get('tradfri', 'securityid')

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.will_set = (topic, "Tradfri went offline!", 1, True)
    #client.on_log = on_log

    return mqtt_srv, mqtt_port, topic, hubip, securityid

def main():
    global flag
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
