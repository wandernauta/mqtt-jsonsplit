#!/usr/bin/env python

import paho.mqtt.client as mqtt
import json
import certifi
import argparse


def split(data, key):
    yield (key, data)

    if isinstance(data, dict):
        for (k, v) in data.items():
            yield from split(v, "{}/{}".format(key, k))
    elif isinstance(data, list):
        for (k, v) in enumerate(data):
            yield from split(v, "{}/{}".format(key, k))


def on_connect(client, userdata, flags, rc):
    for topic in args.topics:
        client.subscribe(topic)


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode('utf-8'))
        for (topic, payload) in split(data, msg.topic):
            if topic != msg.topic:
                client.publish(topic, json.dumps(payload, separators=(',', ':')))
    except ValueError:
        # Ignore invalid JSON
        pass


def on_log(client, userdata, level, buf):
    print(level, buf)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False, prog="mqttsplit")
    parser.add_argument('topics', metavar='TOPIC', type=str, nargs='+', help='topics to subscribe to')
    parser.add_argument('-h', '--host', dest='host', default='localhost', type=str)
    parser.add_argument('-u', '--username', dest='username', metavar='USER', type=str)
    parser.add_argument('-P', '--password', dest='password', metavar='PASS', default='', type=str)
    parser.add_argument('-k', '--keepalive-time', dest='keepalive', type=int, default=60, metavar='SECONDS')
    parser.add_argument('-p', '--port', dest='port', type=int, default=1883)
    parser.add_argument('--ssl', dest='ssl', action='store_true')
    parser.add_argument('--debug', dest='debug', action='store_true')
    parser.add_argument('--help', action='help')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')
    args = parser.parse_args()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    if args.debug:
        client.on_log = on_log

    if args.ssl:
        client.tls_set(certifi.where())

    if args.username:
        client.username_pw_set(args.username, args.password)

    client.connect(args.host, args.port, args.keepalive)
    client.loop_forever()
