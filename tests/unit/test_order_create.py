from src.order import Order
import pytest

class TestOrder:

    @pytest.mark.parametrize("product, email, expected_product, expected_email", [
        ("Happier Than Ever", "test@example.com", "Happier Than Ever", "test@example.com"),
        ("Narrated For You", "test@example.com", "Narrated For You", "test@example.com"),
        ("Happier Than Ever", "", "Happier Than Ever", "Invalid"),
        ("Happier Than Ever", "example.com", "Happier Than Ever", "Invalid"),
        ("Happier Than Ever", "@example.com", "Happier Than Ever", "Invalid"),
        ("Happier Than Ever", "test@example", "Happier Than Ever", "Invalid"),
        ("Happier Than Ever", "test@example.com", "Happier Than Ever", "test@example.com"),
        (None, "test@example.com", None, "test@example.com"),
        (True, "test@example.com", None, "test@example.com"),
        (False, "test@example.com", None, "test@example.com"),
        ({}, "test@example.com", None, "test@example.com"),

    ], ids=[
        "succesfull ordercreation",
        "different product",
        "empty email",
        "no at in email",
        "email starts with at",
        "no dot after at in email",
        "product is None",
        "product is True",
        "product is False",
        "product undefined",
        "product is empty object",
    ])
    def test_order_creation(self, product, email, expected_product, expected_email):
        order = Order(product, email)

        assert order.product == expected_product
        assert order.status == "pending"
        assert order.email == expected_email