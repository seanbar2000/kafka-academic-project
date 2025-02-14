import json
import threading

ROUTE = "data_base.txt"
db_connection_lock = threading.Lock()

def get_all_orders()-> dict:
    try:
        orders_dict = {}
        try:
            with open(ROUTE, "r") as db:
                items_dict = json.load(db)                
        except:
            return orders_dict        

        return items_dict
    except:
        pass

def update_order(order_id, order_status)-> str|None:
    with db_connection_lock:
        orders_dict = get_all_orders()
        updated_order_id = None

        if order_id in orders_dict:
            (orders_dict[order_id])["status"] = order_status
            updated_order_id = order_id

        overwrite_db(orders_dict)
        return updated_order_id


def get_order_by_id(order_id: str)-> dict|None:
    with db_connection_lock:
        orders_dict = get_all_orders()
        for order in orders_dict.values():
            if order["orderId"] == order_id:
                return order
        return None

def addShippingCost(order_dict: dict):
    sum_of_item_costs = order_dict["totalAmount"]
    order_dict["shippingCost"] = round(sum_of_item_costs*2/100 , 2)
    return order_dict

def add_order(order_dict: dict)-> str|None:
    with db_connection_lock:
        order_id = order_dict["orderId"]
        finallized_order_dict = addShippingCost(order_dict)
        all_orders = get_all_orders()
        if order_id in all_orders.keys():
            overwrite_db(all_orders)
            return None
        
        else:
            all_orders.update({order_id: finallized_order_dict})

        overwrite_db(all_orders)
        return order_id


def overwrite_db(data: dict):
    try:
        with open(ROUTE, "w") as db:
            db.write(json.dumps(data))

    except FileNotFoundError:
        print("File not found!")
    except json.JSONDecodeError:
        print("Invalid JSON format!")

    