import pytest
from datetime import datetime, timezone, timedelta
from src.digital_order import DigitalOrder

class TestDigitalOrder:

    @pytest.fixture
    def order(self):
        order = DigitalOrder("Happier Than Ever", "test@example.com")
        return order

    @pytest.mark.parametrize("starting_status, collect_time, expected_status, succeeded",  [
        ("collected", datetime.now(timezone.utc), "collected", False),
        ("collected", datetime.now(timezone.utc) - timedelta(days=1), "collected", False),
        ("collected", datetime.now(timezone.utc) - timedelta(days=14), "collected", False),
    ], ids=[
        "order just collected",
        "order collected day ago",
        "order collected two weeks ago",
    ])
    def test_order_return(self, order, starting_status, collect_time, expected_status, succeeded):
        order.status = starting_status
        order.collected_at = collect_time

        success = order.file_return()

        assert order.status == expected_status
        assert success == succeeded
