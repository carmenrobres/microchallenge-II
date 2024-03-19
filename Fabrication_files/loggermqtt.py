import csv
import time
import datetime
import paho.mqtt.client as mqtt

# MQTT Broker parameters
broker_address = "mqtt-staging.smartcitizen.me"
broker_port = 1883

# CSV file parameters
csv_file = "data.csv"

# MQTT topics to subscribe to
topics = ["lab/mdef/anna"]  # Add your desired topics here

# Callback function to handle MQTT messages
def on_message(client, userdata, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    topic = message.topic
    msg = message.payload.decode("utf-8")

    # Write data to CSV file
    with open(csv_file, mode='a') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, topic, msg])

    print(f"Received message: {msg} on topic: {topic}")

# Set up MQTT client
client = mqtt.Client()
client.on_message = on_message

# Connect to MQTT broker
client.connect(broker_address, broker_port)

# Subscribe to MQTT topics
for topic in topics:
    client.subscribe(topic)

# Start the MQTT loop
client.loop_forever()
