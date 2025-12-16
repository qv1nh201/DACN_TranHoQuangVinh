# backend/app/mqtt_subscriber.py
import json
import time
import logging
import requests
from paho.mqtt import client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "/warehouse/sensor/data"
CLIENT_ID = f"backend_sub_{int(time.time())}"
API_URL = "https://dacn-tranhoquangvinh.onrender.com/api/sensor"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("mqtt_sub")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker")
        client.subscribe(TOPIC)
        logger.info("Subscribed to topic: %s", TOPIC)
    else:
        logger.error("MQTT connect failed with code %s", rc)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
    except Exception as e:
        logger.error("Invalid JSON payload: %s", e)
        return

    # check required fields
    for field in ("device_id", "temperature", "humidity"):
        if field not in data:
            logger.error("Missing field %s in payload %s", field, data)
            return

    try:
        r = requests.post(
            API_URL,
            json={
                "device_id": data["device_id"],
                "temperature": data["temperature"],
                "humidity": data["humidity"],
                "iso_ts": data.get("iso_ts")
            },
            timeout=5
        )

        if r.status_code != 200:
            logger.error("POST failed %s - %s", r.status_code, r.text)
        else:
            logger.info("POST sensor OK (%s)", r.status_code)

    except Exception as e:
        logger.error("POST error: %s", e)

def start_mqtt(broker=BROKER, port=PORT):
    client = mqtt.Client(client_id=CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message

    logger.info("Connecting to broker %s:%s ...", broker, port)
    client.connect(broker, port, keepalive=60)
    logger.info("Starting MQTT loop (broker=%s port=%s topic=%s)", broker, port, TOPIC)
    client.loop_forever()

if __name__ == "__main__":
    start_mqtt()
