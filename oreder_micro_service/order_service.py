import db_connection

topic_order_dict = {}

class ConsumerService:
    

    def add_order(order_dict, topic):
        finallised_order_dict = ConsumerService.addShippingCost(order_dict)
        added_order_id = db_connection.add_order(finallised_order_dict)
        ConsumerService.append_to_order_dict(topic, added_order_id)

    def addShippingCost(order_dict: dict):
        sum_of_item_costs = order_dict["totalAmount"]
        order_dict["shippingCost"] = round(sum_of_item_costs*2/100 , 2)
        return order_dict

    def append_to_order_dict(topic, order_id):
        if topic in topic_order_dict:
            if order_id in topic_order_dict[topic]:
                return
            topic_order_dict[topic].append(order_id)
        else:
            topic_order_dict.update({topic: [order_id]})


    def get_order_by_id(order_id)-> dict:
        return db_connection.get_order_by_id(order_id)
    
    def update_order(update_order_info_dict: dict, topic)-> bool:
        update_result = db_connection.update_order(update_order_info_dict["orderId"], update_order_info_dict["status"])
        if update_result != None:
            ConsumerService.append_to_order_dict(topic, update_result)
            return True
        return False