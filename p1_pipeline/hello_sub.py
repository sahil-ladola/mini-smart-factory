import json

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 1883
TOPIC = "test/hello"

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. Retrying...")
    else:
        print("Connected")
        client.subscribe(TOPIC)

def on_message(client, userdata, message):
    try:
        payload_str = message.payload.decode("utf-8")
        msg_dict = json.loads(payload_str)
    except (UnicodeDecodeError, json.JSONDecodeError) as err:
        print(f"WARNING: invalid message on {message.topic}: {message.payload!r} ({err})")
        return
    print(f"{message.topic}: {msg_dict}")

mqttc = mqtt.Client(CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(BROKER_HOST, BROKER_PORT)
mqttc.loop_forever()