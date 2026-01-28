from src.physical_order import PhysicalOrder
import os
import pytest

class TestPhysicalOrder:
    @pytest.fixture()
    def product(self):
        return "Happier Than Ever"
    
    @pytest.fixture()
    def email(self):
        return "test@example.com"
    
    @pytest.mark.skipif(not os.environ.get("GEOAPIFY_API_KEY"), reason="API Key missing")
    @pytest.mark.parametrize("address, expected_status", [
        ({
            "housenumber": "57",
            "flatnumber": None,
            "street": "Wita Stwosza",
            "postcode": "80-308",
            "city": "Gdańsk",
            "state": "Pomorskie",
            "country": "Polska",
        }, "pending"),
        ({
            "housenumber": "10a",
            "flatnumber": "7",
            "street": "Rakietowa",
            "postcode": "11-111",
            "city": "Mars",
            "state": "Mazowieckie",
            "country": "Polska",
        }, "cancelled"),
    ], ids=[
        "correct address",
        "incorrect address",
    ])
    @pytest.mark.integration
    def test_geoapify_address_verification(self, product, email, address, expected_status):

        order = PhysicalOrder(product, email, address)

        assert order.status == expected_status