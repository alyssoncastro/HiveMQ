import os
import unittest
import paho.mqtt.client as mqtt
import json
import threading
import time
import ssl
from dotenv import load_dotenv


load_dotenv()

broker_address = os.getenv("BROKER_HIVE")
port = int(os.getenv("PORT_HIVE"))
username = os.getenv("HIVE_USER")
password = os.getenv("HIVE_PASS")


#RECEBIMENTO
class TestSimulator(unittest.TestCase):

    def setUp(self):
        self.qos_level = 0

    def test_recebimento(self):
        #inicializa o subscriber
        self.received_message = None
        subscriber = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "test_subscriber")
        subscriber.on_message = self.on_message
        subscriber.username_pw_set(username, password)
        subscriber.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
        subscriber.connect(broker_address, port, 60)
        subscriber.subscribe("sensor/gases", qos=self.qos_level)


        #puublicando no tópico
        simulated_message = '{"sensor": {"name": "Test Sensor"}, "reading": {"CO": 50.0}}'
        publisher = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "test_publisher")
        publisher.username_pw_set(username, password)
        publisher.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
        publisher.connect(broker_address, port, 60)
        publisher.publish("sensor/gases", simulated_message, qos=self.qos_level)


        tempo = time.time()

        while self.received_message is None and time.time() - tempo < 5:
            subscriber.loop_start()
            time.sleep(0.1)

        #verifiacando
        self.assertIsNotNone(self.received_message)


    def on_message(self, client, userdata, message):
        self.received_message = message.payload.decode()

if __name__ == '__main__':
    unittest.main()