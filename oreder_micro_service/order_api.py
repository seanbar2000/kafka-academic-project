import time
from flask import Flask, request
import threading
import json
from order_service import ConsumerService
import order_service as order_service
from kafka import KafkaConsumer


KAFKA_BROKER = "kafka:9092"  # Change if running in Docker
ORDER_CREATE_TOPIC = "create_order"
ORDER_UPDATE_TOPIC = "update_order"

app = Flask(__name__)

received_orders_update_topic = []
received_orders_create_topic = []

def create_creater_consumer():
    try:
        create_order_consumer = KafkaConsumer(
            ORDER_CREATE_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=bytes
        )
        return create_order_consumer
    except:
        return None
    
def create_update_consumer():
    try:
        update_order_consumer = KafkaConsumer(
            ORDER_UPDATE_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=bytes
        )
        return update_order_consumer
    except:
        return None

def consume_orders():
    threading.Thread(target=read_create_orders, daemon=True).start()   
    threading.Thread(target=read_update_orders, daemon=True).start()


def read_create_orders():
    consumer = None
    while consumer == None:
        consumer = create_creater_consumer()
        if consumer == None:
            print("Consumer-updater could not connect. Retrying connection")
            time.sleep(1)

    print("Consumer started. Listening for messages...")
    for message in consumer:
        message_value_data = message.value.decode("utf-8")
        message_value_data = message_value_data.replace("'", '"')
        order_dict = json.loads(message_value_data)
        print(f"Received Order: {order_dict}")  # Debugging Output
        ConsumerService.add_order(order_dict, ORDER_CREATE_TOPIC)

def read_update_orders():
    consumer = None
    while consumer == None:
        consumer = create_update_consumer()
        if consumer == None:
            print("Consumer-creater could not connect. Retrying connection")
            time.sleep(1)

    print("Consumer started. Listening for messages...")
    for message in consumer:
        message_value_data = message.value.decode("utf-8")
        message_value_data = message_value_data.replace("'", '"')
        order_dict = json.loads(message_value_data)
        print(f"Received Order: {order_dict}")  # Debugging Output
        ConsumerService.update_order(order_dict, ORDER_UPDATE_TOPIC)


@app.route("/order-details/<order_id>", methods = ['GET'])
def get_order_by_id(order_id):
    return_order = ConsumerService.get_order_by_id(order_id)
    if return_order:
        return return_order, 200
    return "not found", 404 

@app.route("/getAllOrderIdsFromTopic/<topic_name>", methods=["GET"])
def get_all_order_ids(topic_name):

    if topic_name in order_service.topic_order_dict:
        return order_service.topic_order_dict[topic_name], 200
    
    return "not found", 404

if __name__ == '__main__':
    threading.Thread(target=consume_orders, daemon=True).start()
    app.run(debug=False, host="0.0.0.0" , port=3002)