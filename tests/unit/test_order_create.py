from src.order import Order
import pytest

class TestOrderCreation:

    @pytest.mark.parametrize("product, email, expected_product, expected_email", [
        ("Happier Than Ever", "test@example.com", "Happier Than Ever", "test@example.com"),
        ("Narrated For You", "test@example.com", "Narrated For You", "test@example.com"),
        ("Happier Than Ever", "", "Happier Than Ever", "Invalid"),
        ("Happier Than Ever", "example.com", "Happier Than Ever", "Invalid"),
        ("Happier Than Ever", "@example.com", "Happier Than Ever", "Invalid"),
        ("Happier Than Ever", "test@example", "Happier Than Ever", "Invalid"),
    ], ids=[
        "succesfull ordercreation",
        "different product",
        "empty email",
        "no at in email",
        "email starts with at",
        "no dot after at in email",
    ])
    def test_order_creation(self, product, email, expected_product, expected_email):
        order = Order(product, email)

        assert order.product == expected_product
        assert order.status == "pending"
        assert order.email == expected_email