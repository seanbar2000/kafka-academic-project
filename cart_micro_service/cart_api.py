from flask import Flask, request, jsonify, abort
import requests
from cart_service import CartService
from confluent_kafka import KafkaError
cart_service = CartService()
app = Flask(__name__)

@app.route("/create-order", methods = ['POST'])
def create_order():
    try:
        data = request.get_json()

        if not data or "itemsNum" not in data or "orderId" not in data:
            return jsonify({"error": "Missing order items"}), 400
        
        order_id = data["orderId"]
        response = requests.get(url=f"http://consumer:3002/order-details/{order_id}")

        if response.status_code == 200:
            return jsonify({"error": "Item id already in use"}), 409

        number_of_items = int(data["itemsNum"])

        order_dict = cart_service.create_formatted_order(str(order_id), number_of_items)
        
        return order_dict, 200
    
    except KafkaError as e:
        return {"error": "An error occurred while sending the message to Kafka."}, 500

@app.route("/update-order", methods = ['PUT'])
def update_order():
    data = request.json

    if not data or "orderId" not in data or "status" not in data:
        return jsonify({"error": "Missing orderId or status"}), 400
    
    order_id = data["orderId"]
    new_status = data["status"]
    response = requests.get(url=f"http://consumer:3002/order-details/{order_id}")
    if response.status_code == 404:
        abort(404, description="Not found")

    cart_service.update_order_status(order_id, new_status)
    return jsonify({"message": f"order {order_id} has been updated"}), 200


if __name__ == '__main__':

    app.run(debug=False, host="0.0.0.0", port=3001)