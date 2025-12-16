# backend/app/mqtt_subscriber.py
import json
import time
import logging
from paho.mqtt import client as mqtt

from .firebase_client import save_sensor

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "/warehouse/sensor/data"
CLIENT_ID = f"backend_sub_{int(time.time())}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("mqtt_sub")

def on_connect(client, userdata, flags, rc, properties=None):
    # properties param allowed for newer callback API signature
    if rc == 0:
        logger.info("Connected to MQTT broker")
        client.subscribe(TOPIC)
        logger.info("Subscribed to topic: %s", TOPIC)
    else:
        logger.error("MQTT connect failed with code %s", rc)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        logger.info("Received raw: %s", payload)
        data = json.loads(payload)
        ts = data.get("timestamp")
        if ts and isinstance(ts, str) and ts.isdigit():
            ts_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(int(ts)//1000))
            data["iso_ts"] = ts_iso
        device_id = data.get("device_id", "unknown")
        save_sensor(device_id, data)
        logger.info("Saved to Firebase for device %s", device_id)
    except Exception as e:
        logger.exception("Error processing MQTT message: %s", e)

def start_mqtt(broker=BROKER, port=PORT):
    # Here we force callback_api_version=1 to be compatible with our callback signatures
    # This avoids "Unsupported callback API version" error on some paho-mqtt versions.
    client = mqtt.Client(client_id=CLIENT_ID)


    # attach callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # If your broker requires username/password, uncomment next line:
    # client.username_pw_set("username", "password")
    # If TLS required: client.tls_set()

    logger.info("Connecting to broker %s:%s ...", broker, port)
    client.connect(broker, port, keepalive=60)
    logger.info("Starting MQTT loop (broker=%s port=%s topic=%s)", broker, port, TOPIC)
    client.loop_forever()

if __name__ == "__main__":
    start_mqtt()
