import paho.mqtt.client as mqtt
import json
from paho.mqtt.enums import CallbackAPIVersion


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        print("Connected")
        client.subscribe("test/hello")

def on_message(client, userdata, message):
    payload_str = message.payload.decode("utf-8")
    msg_dic = json.loads(payload_str)
    print(message.topic)
    print(msg_dic)

mqttc = mqtt.Client(CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("127.0.0.1", 1883)
mqttc.loop_forever()