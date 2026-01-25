import re

status_changes = {"pending" : "ready", "ready" : "shipping", "shipping" : "collected", "collected" : "collected"}

class Order:
    def __init__(self, product, email):
        self.product = product if isinstance(product, str) else None
        self.status = "pending"
        self.email = "Invalid" if not re.match(r"[^@]+@[^@]+\.[^@]+", email)  else email

    def change_status(self):
        self.status = status_changes[self.status]