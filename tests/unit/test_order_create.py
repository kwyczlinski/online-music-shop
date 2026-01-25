from src.order import Order

class TestOrderCreation:

    def test_order_creation(self):
        order = Order("Happier Than Ever")
        assert order.product == "Happier Than Ever"
        assert order.status == "pending"