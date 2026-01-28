from src.order import Order

necessary_address_keys = ["housenumber","street","postcode","city","state","country"]

class PhysicalOrder(Order):
    def __init__(self, product, email: str, address: dict[str, str | None]):
        super().__init__(product, email)
        self.address = address
        self.status = "pending" if self.verify_address(address) else "cancelled"

    def verify_address(self, address: dict[str, str | None]):
        flat_number: str | None = address.get("flatnumber", None)
        if (flat_number != None and (not isinstance(flat_number, str) or len(flat_number.strip()) == 0)):
            return False
        
        for key in necessary_address_keys:
            value: str | None = address.get(key, None)

            if value == None or (value != None and (not isinstance(value, str) or len(value.strip()) == 0)):
                return False
        
        return True