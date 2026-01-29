from src.digital_order import DigitalOrder
from src.physical_order import PhysicalOrder
from src.custom_errors import *

orderType = DigitalOrder | PhysicalOrder

class OrderRegistry:
    def __init__(self) -> None:
        self.active_registry: list[orderType] = []
        self.order_history: list[orderType] = []

    def add_order(self, order: orderType) -> bool:
        if not isinstance(order, (DigitalOrder, PhysicalOrder)):
            return False
        
        if order.status in ["collected", "cancelled", "returned"]:
            self.order_history.append(order)
        else:
            self.active_registry.append(order)

        return True

    def get_active_orders(self) -> list[orderType]:
        return self.active_registry
    
    def get_active_orders_count(self) -> int:
        return len(self.active_registry)
    
    def get_history_orders(self) -> list[orderType]:
        return self.order_history
    
    def get_history_orders_count(self) -> int:
        return len(self.order_history)
    
    def get_order(self, order_id: str) -> orderType | None:
        found = next((order for order in self.active_registry if order.id == order_id), None)
        if found:
            return found
        
        return next((order for order in self.order_history if order.id == order_id), None)
    
    def get_orders_by_email(self, email: str) -> list[str]:
        return [order.id for i,order in enumerate(self.active_registry) if order.email == email]

    def cancel_order(self, order_id: str) -> bool:
        list_id = next((id for id in range(len(self.active_registry)) if self.active_registry[id].id == order_id), None)
        if list_id == None:
            return False
        
        order = self.active_registry.pop(list_id)
        can_cancel = order.cancel()

        if can_cancel:
            self.order_history.append(order)
        else:
            self.active_registry.append(order)

        return can_cancel

    def advance_order(self, order_id: str) -> str | None:
        order = next((order for order in self.active_registry if order.id == order_id), None)
        if not order:
            return None
        order.change_status()
        return order.status

    def return_order(self, order_id: str) -> bool:
        list_id = next((id for id in range(len(self.order_history)) if self.order_history[id].id == order_id), None)
        if list_id == None:
            raise OrderNotFoundError(f"Orders with id {order_id} not found in past orders")
        
        order = self.order_history.pop(list_id)

        if isinstance(order, DigitalOrder):
            self.order_history.append(order)
            raise ReturnPolicyViolation("Digital orders can not be returned.")
        
        can_return = order.file_return()

        if can_return:
            self.active_registry.append(order)
        else:
            self.order_history.append(order)
            if order.status == "collected":
                raise ReturnPolicyViolation("Order is past the 14-day return window.")
            else:
                raise ReturnPolicyViolation("Only collected orders are eligible for return.")
        
        return can_return
    
    def update_email(self, order_id: str, new_email: str) -> bool:
        list_id = next((id for id in range(len(self.active_registry)) if self.active_registry[id].id == order_id), None)
        if list_id == None:
            return False
        
        order = self.active_registry[list_id]
    
        isValid = order.verify_email(new_email)

        if isValid:
            order.email = new_email
            return True
        return False
    
    def update_address(self, order_id: str, new_address: dict[str, str | None]) -> bool:
        list_id = next((id for id in range(len(self.active_registry)) if self.active_registry[id].id == order_id), None)
        if list_id == None:
            return False
        
        order = self.active_registry[list_id]

        if not isinstance(order, PhysicalOrder) or order.status in ["shipping", "collected", "returning", "returned"]:
            return False

        isValid = order.verify_address(new_address) and order.address_exists(new_address)

        if isValid:
            order.address = new_address
            return True
        return False
