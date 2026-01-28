from src.order import Order
import requests
from requests.structures import CaseInsensitiveDict
from urllib.parse import quote
from dotenv import load_dotenv
import os

load_dotenv(".env")
GEOAPIFY_API_KEY = os.environ.get("GEOAPIFY_API_KEY")

NECESSARY_ADDRESS_KEYS = ["housenumber","street","postcode","city","state","country"]
ADDRESS_SEARCH_ORDER = ["housenumber", "street", "city", "state", "postcode", "country"]

class PhysicalOrder(Order):
    def __init__(self, product, email: str, address: dict[str, str | None]):
        super().__init__(product, email)
        self.address = address
        self.status = "pending" if self.verify_address(address) and self.address_exists(address) else "cancelled"

    def verify_address(self, address: dict[str, str | None]):
        flat_number: str | None = address.get("flatnumber", None)
        if (flat_number != None and (not isinstance(flat_number, str) or len(flat_number.strip()) == 0)):
            return False
        
        for key in NECESSARY_ADDRESS_KEYS:
            value: str | None = address.get(key, None)

            if value == None or (value != None and (not isinstance(value, str) or len(value.strip()) == 0)):
                return False
        
        return True
            
    def address_exists(self, address: dict[str, str | None]):
        address_parts = []

        for key in ADDRESS_SEARCH_ORDER:
            value = address.get(key)
            if value and isinstance(value, str) and value.strip():
                address_parts.append(value.strip())
        address_string = " ".join(address_parts)
        
        url_text = quote(address_string)
        url = f"https://api.geoapify.com/v1/geocode/search?text={url_text}&apiKey={GEOAPIFY_API_KEY}"
        
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                return True
            
            data = resp.json()

            places = data.get("features", [])

            for place in places:
                details = place.get("properties", {})
                
                rank = details.get("rank", {})
                confidence = rank.get("confidence", 0)

                if confidence >= 0.7:
                    return True
            
            return False

        except (requests.exceptions.RequestException, ValueError, KeyError):
            return True