from src.order import Order
import pytest

class TestOrder:

    @pytest.mark.parametrize("product, email, expected_product, expected_email, expected_status", [
        ("Happier Than Ever", "test@example.com", "Happier Than Ever", "test@example.com", "pending"),
        ("Narrated For You", "test@example.com", "Narrated For You", "test@example.com", "pending"),
        ("Happier Than Ever", "", "Happier Than Ever", "Invalid", "cancelled"),
        ("Happier Than Ever", "example.com", "Happier Than Ever", "Invalid", "cancelled"),
        ("Happier Than Ever", "@example.com", "Happier Than Ever", "Invalid", "cancelled"),
        ("Happier Than Ever", "test@example", "Happier Than Ever", "Invalid", "cancelled"),
        ("Happier Than Ever", "test@example.com", "Happier Than Ever", "test@example.com", "cancelled"),
        (None, "test@example.com", None, "test@example.com", "cancelled"),
        (True, "test@example.com", None, "test@example.com", "cancelled"),
        (False, "test@example.com", None, "test@example.com", "cancelled"),
        ({}, "test@example.com", None, "test@example.com", "cancelled"),

    ], ids=[
        "succesfull order creation",
        "succesfull with different product",
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
    def test_order_creation(self, product, email, expected_product, expected_email, expected_status):
        order = Order(product, email)

        assert order.product == expected_product
        assert order.status == expected_status
        assert order.email == expected_email

    @pytest.mark.parametrize("advance_times, starting_status, expected_status", [
        (1, "pending", "ready"),
        (2, "pending", "shipping"),
        (3, "pending", "collected"),
        (4, "pending", "collected"),
        (1, "cancelled", "cancelled"),
        (4, "cancelled", "cancelled"),
    ], ids=[
        "change to ready",
        "change to shipping",
        "change to collected",
        "can not go past collected",
        "order is cancelled",
        "many chages to cancelled",
    ])
    def test_status_change(self, advance_times, starting_status, expected_status):
        order = Order("Happier Than Ever", "test@example.com")
        order.status = starting_status

        for i in range(advance_times):
            order.change_status()
        
        assert order.status == expected_status