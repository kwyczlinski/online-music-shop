import re
from datetime import datetime, timezone, timedelta
import uuid

status_changes = {"pending" : "ready", "ready" : "shipping", "shipping" : "collected", "collected" : "collected", "cancelled" : "cancelled", "returning" : "returned", "returned" : "returned"}

class Order:
    def __init__(self, product, email):
        self.product = product if self.verify_product(product) else None
        self.email: str = email if self.verify_email(email)  else "Invalid"
        self.status: str = "pending" if self.product and self.verify_email(email) else "cancelled"
        self.collected_at = None
        self.id: str = str(uuid.uuid4())


    def verify_product(self, product) -> bool:
        return True if isinstance(product, str) and len(product) > 0 else False

    def verify_email(self, email) -> bool:
        return True if re.match(r"[^@]+@[^@]+\.[^@]+", email) else False

    def change_status(self) -> None:
        if self.status == "shipping":
            self.collected_at = datetime.now(timezone.utc)
        self.status = status_changes.get(self.status, "cancelled")

    def cancell(self) -> bool:
        if ["pending", "ready"].count(self.status) > 0:
            self.status = "cancelled"
            return True
        return False
    
    def file_return(self) -> bool:
        if self.collected_at and datetime.now(timezone.utc) <= self.collected_at + timedelta(days=14):
            self.status = "returning"
            return True
        return False

