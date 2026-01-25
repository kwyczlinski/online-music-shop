import re

class Order:
    def __init__(self, product, email):
        self.product = product
        self.status = "pending"
        self.email = "Invalid" if not re.match('[^@]+@[^@]+/.[^@]+', email)  else email