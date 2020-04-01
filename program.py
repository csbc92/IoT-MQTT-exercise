import paho.mqtt.client as mqtt
import time
import util
import json
import random
import math
import threading

host = "localhost"
port = 1883
keep_alive = 60 # seconds

# Wrapper function for returning the expected callback given the topic
def subscribe(topic):
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(topic) # for example: "$SYS/broker/uptime"

    return on_connect # Return the function..

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def uptime_publish_thread():
    # connect to broker
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(host, port, keep_alive)

    while True:
        # Get uptime from laptop
        uptime = util.get_uptime(util.get_uptime_seconds())
        print("("+str(uptime[0])+","+str(uptime[1])+","+str(uptime[2])+","+str(uptime[3])+")")

        # Timestamp in ms
        timestamp = int(time.time_ns() * math.pow(10, -6))

        # MQTT payload
        payload = json.dumps({
            u"timestamp": timestamp,
            u"uptime":
                {
                    u"days": uptime[0],
                    u"hours": uptime[1],
                    u"minutes": uptime[2],
                    u"seconds": uptime[3]
                }
        })

        # Publish to mylaptop/uptime
        client.publish("mylaptop/uptime", payload, qos=0) # QoS0 -> deliver no more than once without receipt
                                                          # QoS1 -> is delivered as often as necessary until the subscriber has confirmed receipt
                                                          # QoS2 -> ensures that the subscriber receives the message exactly once
        time.sleep(5)

def temperature_celcius_publish_thread():
    # connect to broker
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(host, port, keep_alive)

    while True:
        # Timestamp in ms
        timestamp = int(time.time_ns() * math.pow(10, -6))

        # MQTT payload
        payload = json.dumps({
            u"timestamp": timestamp,
            u"temperature": round(15 + (random.random() * 19), 2)  # Random number from 15 to 34.99
        })

        # Publish to mylaptop/uptime
        client.publish("myroom/sensors/temperature/c", payload, qos=0)  # QoS0 -> deliver no more than once without receipt
                                                                        # QoS1 -> is delivered as often as necessary until the subscriber has confirmed receipt
                                                                        # QoS2 -> ensures that the subscriber receives the message exactly once
        time.sleep(5)


def on_msg(client, userdata, msg):
    myDict = json.loads(msg.payload)
    timestamp = myDict['timestamp']
    celsius = myDict['temperature']

    # MQTT payload
    payload = json.dumps({
        u"timestamp": timestamp, # Reuse the timestamp, since this is merely a conversion of a previous celsius record
        u"temperature": util.celsius_to_fahrenheit(celsius)
    })

    client.publish("myroom/sensors/temperature/f", payload, qos=0)  # QoS0 -> deliver no more than once without receipt
                                                                    # QoS1 -> is delivered as often as necessary until the subscriber has confirmed receipt
                                                                    # QoS2 -> ensures that the subscriber receives the message exactly once


def temperature_fahrenheit_publish_thread():
    # connect to broker
    client = mqtt.Client()
    client.on_connect = subscribe("myroom/sensors/temperature/c")
    client.on_message = on_msg
    client.connect(host, port, keep_alive)
    client.loop_forever()


thread_uptime_publish = threading.Thread(target=uptime_publish_thread)
thread_celsius = threading.Thread(target=temperature_celcius_publish_thread)
#thread_fahrenheit = threading.Thread(target=temperature_fahrenheit_publish_thread)

thread_uptime_publish.start()
thread_celsius.start()
temperature_fahrenheit_publish_thread()