from src.digital_order import DigitalOrder
from src.order_registry import OrderRegistry
from src.physical_order import PhysicalOrder
import pytest
from datetime import datetime, timezone, timedelta
from src.custom_errors import *

class TestOrderRegistry:
    @pytest.fixture()
    def registry(self):
        registry: OrderRegistry = OrderRegistry()
        return registry
    
    @pytest.fixture()
    def order(self):
        order = DigitalOrder("Happier Than Ever", "test@example.com")
        return order

    @pytest.fixture()
    def physical_order(self):
        physical_order = PhysicalOrder("Happier Than Ever", "test@example.com", {})
        return physical_order
    
    @pytest.fixture()
    def orders(self):
        orders = [DigitalOrder("Happier Than Ever", "test@example.com"), DigitalOrder("Narrated For You", "test@test.com"), DigitalOrder("Those Two Windows", "test@example.com"), DigitalOrder("Irenka", "sanah@sanah.com")]
        return orders

    def test_registry_creation(self, registry: OrderRegistry):
        assert registry.active_registry == []
        assert registry.order_history == []

    @pytest.mark.parametrize("valid_orders, invalid_orders, expected_active_count, expected_history_count", [
        ([], [], 0, 0),
        ([DigitalOrder("Happier Than Ever", "test@example.com"), DigitalOrder("Narrated For You", "test@test.com")], [], 2, 0),
        ([], [DigitalOrder("Happier Than Ever", "test@.com")], 0, 1),
        ([DigitalOrder("Narrated For You", "test@test.com"), DigitalOrder("Those Two Windows", "test@example.com"), DigitalOrder("Irenka", "sanah@sanah.com")], [DigitalOrder("Happier Than Ever", "test@.com"), DigitalOrder("Narrated For You", "@test.com")], 3, 2),
        ([DigitalOrder("Happier Than Ever", "test@example.com")], [DigitalOrder("Happier Than Ever", "test@.com")], 1, 1),
        ([[], {}], [], 0, 0),
        ([True], [False], 0, 0),
        (["music"], [], 0, 0),
        ([], [None], 0, 0),
    ], ids=[
        "no orders",
        "two valid orders",
        "one invalid order",
        "mixed orders",
        "one of each",
        "bad types list and dict",
        "bad types bool",
        "bad types str",
        "bad types None",
    ])
    def test_add_orders(self, registry: OrderRegistry, valid_orders, invalid_orders, expected_active_count, expected_history_count):
        for order in valid_orders:
            registry.add_order(order)
        
        for order in invalid_orders:
            registry.add_order(order)

        num_active = registry.get_active_orders_count()
        num_history = registry.get_history_orders_count()

        assert num_active == expected_active_count
        assert num_history == expected_history_count

    @pytest.mark.parametrize("starting_status, advance_times, expected_status", [
        ("pending", 0, "pending"),
        ("pending", 1, "ready"),
        ("pending", 2, "shipping"),
        ("pending", 3, "collected"),
        ("pending", 4, "collected"),
        ("returning", 0, "returning"),
        ("returning", 1, "returned"),
        ("returning", 2, "returned"),
        ("cancelled", 1, "cancelled"),
    ], ids=[
        "stay pending",
        "to ready",
        "to shipping",
        "to collected",
        "can not go past collected",
        "stay returning",
        "to returned",
        "can not go past returned",
        "can not change cancelled",
    ])
    def test_advance_order(self, registry: OrderRegistry, order: DigitalOrder, starting_status: str, advance_times: int, expected_status: str):
        order.status = starting_status
        registry.add_order(order)

        for _ in range(advance_times):
            registry.advance_order(order.id)

        found = registry.get_order(order.id)

        assert found != None
        assert found.status == expected_status 

    @pytest.mark.parametrize("email, expected_number_found", [
        ("test@example.com", 2),
        ("test@test.com", 1),
        ("margaret@margaret.com", 0),
        ({None}, 0),
        ([], 0),
        ("      ", 0),
        ("", 0),
        (True, 0),
        (False, 0),
        (None, 0),
    ], ids=[
        "many orders found",
        "single order found",
        "None orders found",
        "bad type obj",
        "bad type list",
        "bad type white spaces",
        "bad type empty string",
        "bad type True",
        "bad type False",
        "bad type None",
    ])
    def test_order_find_by_email(self, registry: OrderRegistry, orders: list[DigitalOrder], email: str, expected_number_found: int):
        for order in orders:
            registry.add_order(order)
        
        result = registry.get_orders_by_email(email)

        num_orders = len(result)

        for order.id in result:
            order = registry.get_order(order.id)
            assert order != None
            assert order.email == email

        assert num_orders == expected_number_found

    @pytest.mark.parametrize("starting_status, expected_result, inHistory", [
        ("pending", True, True),
        ("ready", True, True),
        ("shipping", False, False),
        ("collected", False, True),
        ("cancelled", False, True),
        ("returning", False, False),
        ("returned", False, True),
    ], ids=[
        "successfully cancelled when pending",
        "successfully cancelled when ready",
        "tried to cancel when shipping",
        "tried to cancel when collected",
        "tried to cancel when cancelled",
        "tried to cancel when returning",
        "tried to cancel when returned",
    ])
    def test_cancel_order(self, registry: OrderRegistry, order: DigitalOrder, starting_status: str, expected_result: bool, inHistory: bool):
        order.status = starting_status
        registry.add_order(order)
        
        result = registry.cancel_order(order.id)

        assert result == expected_result
        if inHistory:
            assert order in registry.order_history
        else:
            assert order in registry.active_registry

    @pytest.mark.parametrize("starting_status, expected_error, expected_msg", [
        ("pending", OrderNotFoundError, "not found in past orders"),
        ("ready", OrderNotFoundError, "not found in past orders"),
        ("shipping", OrderNotFoundError, "not found in past orders"),
        ("cancelled", ReturnPolicyViolation, "eligible for return."),
        ("returned", ReturnPolicyViolation, "eligible for return."),
    ], ids=[
        "tried to return when pending",
        "tried to return when ready",
        "tried to return when shipping",
        "tried to return when cancelled",
        "tried to return when returned",
    ])
    def test_fail_return_order(self, registry, physical_order, starting_status, expected_error, expected_msg):
        physical_order.status = starting_status
        physical_order.collected_at = datetime.now(timezone.utc) - timedelta(hours=1)
        
        if starting_status in ["collected", "cancelled", "returned"]:
            registry.order_history.append(physical_order)
        else:
            registry.active_registry.append(physical_order)

        with pytest.raises(expected_error) as excinfo:
            registry.return_order(physical_order.id)
        assert expected_msg in str(excinfo.value)

    def test_succesfull_return(self, registry: OrderRegistry, physical_order: PhysicalOrder):
        physical_order.status = "collected"
        physical_order.collected_at = datetime.now(timezone.utc) - timedelta(hours=1)
        registry.order_history.append(physical_order)

        result = registry.return_order(physical_order.id)

        assert result is True
        assert physical_order in registry.active_registry

    def test_can_not_return_digital(self, registry: OrderRegistry, order: DigitalOrder):
        order.status = "collected"
        order.collected_at = datetime.now(timezone.utc) - timedelta(hours=1)
        registry.order_history.append(order)

        with pytest.raises(ReturnPolicyViolation) as excinfo:
            registry.return_order(order.id)
        
        assert "Digital orders can not be returned." in str(excinfo.value)
        assert order in registry.order_history
        assert registry.get_active_orders_count() == 0
