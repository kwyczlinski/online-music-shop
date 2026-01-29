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

    @pytest.fixture()
    def mock_api(self, mocker):
        return mocker.patch("src.physical_order.PhysicalOrder.address_exists", return_value=True)

    @pytest.fixture
    def valid_address(self):
        valid_address = {"housenumber": "12","flatnumber": "3","street": "Długa","postcode": "80-001","city": "Gdańsk","state": "Pomorskie","country": "Polska"}
        return valid_address

    @pytest.fixture
    def invalid_address(self):
        invalid_address =  {"housenumber": None,"city": ""}
        return invalid_address

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

        expected_active = [order for i,order in enumerate(valid_orders) if isinstance(order, DigitalOrder)]
        expected_history = [order for i,order in enumerate(invalid_orders) if isinstance(order, DigitalOrder)]

        active = registry.get_active_orders()
        num_active = registry.get_active_orders_count()
        history = registry.get_history_orders()
        num_history = registry.get_history_orders_count()

        assert active == expected_active
        assert num_active == expected_active_count
        assert history == expected_history
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
    def test_fail_return_order(self, registry: OrderRegistry, physical_order: PhysicalOrder, starting_status: str, expected_error, expected_msg: str):
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

    def test_past_return_date(self, registry: OrderRegistry, physical_order: PhysicalOrder):
        physical_order.status = "collected"
        physical_order.collected_at = datetime.now(timezone.utc) - timedelta(days=31)
        registry.order_history.append(physical_order)
        
        with pytest.raises(ReturnPolicyViolation) as excinfo:
            registry.return_order(physical_order.id)
        assert "Order is past the 14-day return window." in str(excinfo.value)

    @pytest.mark.parametrize("new_email, expected_result", [
        ("new.test@example.com", True),
        ("test.test@test.co.uk", True),
        ("example", False),
        ("@example.com", False),
        ("example@.com", False),
        ("", False),
        ("    ", False),
        (None, False),
    ], ids=[
        "valid email",
        "advanced valid email",
        "missing at",
        "starts with at",
        "no dot",
        "empty string",
        "white spaces",
        "None value",
    ])
    def test_email_change(self, registry: OrderRegistry, order: DigitalOrder, new_email: str, expected_result: bool):
        registry.active_registry.append(order)
        original_email = order.email
        
        result = registry.update_email(order.id, new_email)
        
        assert result == expected_result
        if expected_result:
            assert order.email == new_email
        else:
            assert order.email == original_email

    def test_fail_email_change_no_id(self, registry: OrderRegistry):
        result = registry.update_email("non-existant-id", "test@example.com")
        assert result == False

    @pytest.mark.parametrize("starting_status, use_valid_address, expected_result", [
        ("pending", True, True),
        ("ready", True, True),
        ("shipping", True, False),
        ("collected", True, False),
        ("returning", True, False),
        ("returned", True, False),
        ("pending", False, False),
        ("ready", False, False),
    ], ids=[
        "update when pending",
        "update when ready",
        "can not update when shipping",
        "can not update when collected",
        "can not update when returning",
        "can not update when returned",
        "fail invalid address when pending",
        "fail invalid address when ready"
    ])
    def test_address_change(self, registry: OrderRegistry, physical_order: PhysicalOrder, mock_api, valid_address, invalid_address, starting_status, use_valid_address, expected_result):
        physical_order.status = starting_status
        registry.active_registry.append(physical_order)
        target_address = valid_address if use_valid_address else invalid_address
        
        result = registry.update_address(physical_order.id, target_address)
        
        assert result == expected_result
        if expected_result:
            assert physical_order.address == target_address
        else:
            assert physical_order.address != target_address

    def test_can_not_change_digital_order_address(self, registry: OrderRegistry, order: DigitalOrder, valid_address):
        registry.active_registry.append(order)
        result = registry.update_address(order.id, valid_address)
        assert result == False

    def test_fail_address_change_no_id(self, registry: OrderRegistry, valid_address):
        result = registry.update_address("non-existant-id", valid_address)
        assert result == False