import json
import time

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 1883
TOPIC = "test/hello"
NUM_MESSAGES = 5

mqttc = mqtt.Client(CallbackAPIVersion.VERSION2)

mqttc.connect(BROKER_HOST, BROKER_PORT)

mqttc.loop_start()

for i in range(NUM_MESSAGES):
    data = {"machine": "M1", "temp": 300 + i, "n": i}
    payload = json.dumps(data)
    info = mqttc.publish(TOPIC, payload)
    info.wait_for_publish()
    print(f"Sent message {i}: {payload}")
    time.sleep(1)

mqttc.disconnect()
mqttc.loop_stop()