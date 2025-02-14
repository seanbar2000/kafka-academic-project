from flask import jsonify, abort
import random
from datetime import datetime
import uuid
from confluent_kafka import Producer
import requests

KAFKA_BROKER = "kafka:9092"
ORDER_CREATE_TOPIC = "create_order"
ORDER_UPDATE_TOPIC = "update_order"

class CartService:
    def __init__(self):
        self.producer = Producer({'bootstrap.servers': KAFKA_BROKER, 'retries': 5})

    def create_formatted_order(self, order_id: str, number_of_items: int):
        list_of_items, total_amount = self.generateItemList(number_of_items)
        order_dict = {
            "orderId" : order_id,
            "customerId" : str(uuid.uuid4()),
            "orderDate" : datetime.now().isoformat(),
            "items" : list_of_items,
            "totalAmount" : total_amount,
            "currency": "USD",
            "status": "New"
        }
        self.producer.produce(ORDER_CREATE_TOPIC, key=order_dict["orderId"], value=str(order_dict))
        self.producer.flush()
        return jsonify(order_dict)


    def update_order_status(self, order_id: str, new_status: str):
        update_order_dict = {"orderId": order_id, "status": new_status}
        self.producer.produce(ORDER_UPDATE_TOPIC, key=order_id, value=str(update_order_dict))
        self.producer.flush()


    def generateItemList(self, number_of_items: int):
        items_list = []
        total_amount = 0.0
        for index in range(number_of_items):
            items_list.append({"itemId": str(uuid.uuid4()), "quantity": random.randint(1,10), "price": round(random.uniform(1, 10), 2)})
            total_amount += items_list[index]["price"]
        return items_list, round(total_amount, 2)
