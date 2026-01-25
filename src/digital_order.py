from src.order import Order

class DigitalOrder(Order):
    def __init__(self, product, email):
        super().__init__(product, email)

    def file_return(self) -> bool:
        return False
