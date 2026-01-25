import re

status_changes = {"pending" : "ready", "ready" : "shipping", "shipping" : "collected", "collected" : "collected", "cancelled" : "cancelled"}

class Order:
    def __init__(self, product, email):
        self.product = product if self.verify_product(product) else None
        self.email = email if self.verify_email(email)  else "Invalid"
        self.status = "pending" if self.product != None and self.verify_email(email) else "cancelled"

    def verify_product(self, product) -> bool:
        return True if isinstance(product, str) and len(product) > 0 else False

    def verify_email(self, email) -> bool:
        return True if re.match(r"[^@]+@[^@]+\.[^@]+", email) else False

    def change_status(self) -> None:
        self.status = status_changes.get(self.status, "cancelled")

    def cancell(self) -> bool:
        if ["pending", "ready"].count(self.status) > 0:
            self.status = "cancelled"
            return True
        return False
