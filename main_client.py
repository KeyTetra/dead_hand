import paho.mqtt.client as mqtt
import time
import random

# MQTT broker address and port
broker_address = "192.168.4.1"
broker_port = 1883

# # MQTT credentials
username = "alice"
password = "secret"


# Function to handle incoming messages
def on_message(client, userdata, message):
    print("client:", client)
    print("topic:", message.topic)
    print("userdata:", userdata)
    print("Received message:", str(message.payload.decode("utf-8")))


# Create MQTT client
client = mqtt.Client()

# Set username and password
client.username_pw_set(username, password)

# Assign the message handling function
client.on_message = on_message

# Connect to MQTT broker
client.connect(broker_address, broker_port)

# Subscribe to a topic
topic = "Python"
client.subscribe(topic)

# Publish random messages periodically with different QoS
while True:
    random_message = f"Message {random.randint(1, 100)}"

    print(client.publish(topic, random_message))
    print(f"Published message: {random_message}")
    time.sleep(1)  # Publish every 1 seconds

# Start the MQTT loop
client.loop_forever()