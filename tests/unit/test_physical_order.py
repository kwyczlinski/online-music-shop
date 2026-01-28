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
            "city": "Gdańsk",
            "state": "Pomorskie",
            "country": "Polska",
        }
        return valid_address
    
    @pytest.fixture()
    def product(self):
        return "Happier Than Ever"
    
    @pytest.fixture()
    def email(self):
        return "test@example.com"
    
    @pytest.fixture()
    def mock_api(self, mocker):
        return mocker.patch("src.physical_order.PhysicalOrder.address_exists", return_value=True)

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
    def test_order_creation_address(self, mock_api, product, email, valid_address, changes, expected_status):
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
    def test_missing_address_param(self, mock_api, product, email, valid_address, delete, expected_status):
        valid_address.pop(delete)

        order = PhysicalOrder(product, email, valid_address)

        assert order.status == expected_status

    @pytest.mark.parametrize("api_resp, address, expected_status", [
        ({"features": [{"properties": {"rank": {"confidence": 0.9}}}]},
        {
            "housenumber": "57",
            "flatnumber": None,
            "street": "Wita Stwosza",
            "postcode": "80-308",
            "city": "Gdańsk",
            "state": "Pomorskie",
            "country": "Polska",
        }, "pending"),
        ({"features": [{"properties": {"rank": {"confidence": 0.25}}}]},
        {
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
    def test_address_exists(self, mocker, product, email, api_resp, address, expected_status):
        
        mock_get = mocker.patch("src.physical_order.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = api_resp

        order = PhysicalOrder(product, email, address)

        assert order.status == expected_status

        args, kwargs = mock_get.call_args
        assert "api.geoapify.com" in args[0]