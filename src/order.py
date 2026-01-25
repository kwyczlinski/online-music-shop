import re

class Order:
    def __init__(self, product, email):
        self.product = product if isinstance(product, str) else None
        self.status = "pending"
        self.email = "Invalid" if not re.match(r"[^@]+@[^@]+\.[^@]+", email)  else email

    def change_status(self):
        if self.status == "pending":
            self.status = "ready"
        elif self.status == "ready":
            self.status = "shipping"
        elif self.status == "shipping":
            self.status = "collected"
