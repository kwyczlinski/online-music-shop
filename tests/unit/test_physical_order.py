from src.physical_order import PhysicalOrder
import pytest

class TestPhysicalOrder:
    @pytest.fixture()
    def valid_address(self):
        valid_address: dict[str, str | None] = {
            "housenumber": "57",
            "flatnumber": "2.16",
            "street": "Wita Stwosza",
            "postcode": "80-308",
            "city": "Gdansk",
            "state": "Pomerian",
            "country": "Poland",
        }
        return valid_address
    
    @pytest.fixture()
    def product(self):
        return "Happier Than Ever"
    
    @pytest.fixture()
    def email(self):
        return "test@example.com"

    @pytest.mark.parametrize("changes, expected_status", [
        ({}, "pending"),
        ({"flatnumber" : None}, "pending"),
        ({"housenumber" : None}, "cancelled"),
        ({"housenumber" : True}, "cancelled"),
        ({"flatnumber" : False}, "cancelled"),
        ({"street" : None}, "cancelled"),
        ({"street" : True}, "cancelled"),
        ({"postcode" : None}, "cancelled"),
        ({"postcode" : {}}, "cancelled"),
        ({"city" : None}, "cancelled"),
        ({"city" : ""}, "cancelled"),
        ({"state" : None}, "cancelled"),
        ({"state" : []}, "cancelled"),
        ({"country" : None}, "cancelled"),
        ({"country" : 2}, "cancelled"),
        ({"country" : '''     
    '''}, "cancelled"),
    ], ids=[
        "correct address",
        "correct address not a flat",
        "None house number",
        "bad type house number",
        "bad type flat number",
        "None street",
        "bad type street",
        "None postcode",
        "bad type postcode",
        "None city",
        "bad type city",
        "None state",
        "bad type state",
        "None country",
        "bad type country",
        "bad type whitespaces",      
    ])
    def test_order_creation_address(self, product, email, valid_address, changes, expected_status):
        test_address = {**valid_address, **changes}
        order = PhysicalOrder(product, email, test_address)

        assert order.status == expected_status
        if expected_status == "pending":
            assert order.address == test_address

    @pytest.mark.parametrize("delete, expected_status", [
        ("flatnumber", "pending"),
        ("housenumber", "cancelled"),
        ("street", "cancelled"),
        ("postcode", "cancelled"),
        ("city", "cancelled"),
        ("state", "cancelled"),
        ("country", "cancelled"),
    ], ids=[
        "missing flatnumber but correct",
        "missing housenumber",
        "missing street",
        "missing postcode",
        "missing city",
        "missing state",
        "missing country"
    ])
    def test_missing_address_param(self, product, email, valid_address, delete, expected_status):
        valid_address.pop(delete)

        order = PhysicalOrder(product, email, valid_address)

        assert order.status == expected_status