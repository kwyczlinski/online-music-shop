from src.order import Order

class TestOrderCreation:

    def test_order_creation(self):
        order = Order("Happier Than Ever", "test@example.com")

        assert order.product == "Happier Than Ever"
        assert order.status == "pending"
    
    def test_empty_email(self):
        order = Order("Happier Than Ever", "")

        assert order.email == "Invalid"

    def test_empty_email(self):
        order = Order("Happier Than Ever", "")

        assert order.email == "Invalid"

    def test_no_at_in_email(self):
        order = Order("Happier Than Ever", "example.email")

        assert order.email == "Invalid"

    def test_at_starts_email(self):
        order = Order("Happier Than Ever", "@example.com")

        assert order.email == "Invalid"

    def test_no_dot_after_at_in_email(self):
        order = Order("Happier Than Ever", "test@example")

        assert order.email == "Invalid"
