from behave import given, when, then, step
from urllib.parse import quote
from unittest.mock import patch

STATUSES = ["pending", "ready", "shipping", "collected", "cancelled", "returning", "returned"]
REGISTRIES = ["active", "history"]
ADDRESS_KEYS = ["housenumber", "flatnumber", "street", "postcode", "city", "state", "country"]
ORDER_TYPES = ["digital", "physical"]

PRODUCT = "Aglow (Intro)"
EMAIL = "Karamel@Kel.com"
ADDRESS = {"housenumber": "57","flatnumber": None,"street": "Wita Stwosza","postcode": "80-308","city": "Gdańsk","state": "Pomorskie","country": "Polska"}

address_mock = patch("src.physical_order.PhysicalOrder.address_exists", return_value=True)
address_mock.start()

@given('{registry} registry is empty') # type: ignore
def clear_active_registry(context, registry):
    if registry.lower() not in REGISTRIES:
        raise ValueError(f"Invalid registry: {registry}. Must be one of {REGISTRIES}.")
    
    url = f"{context.base_url}/api/orders/{'active' if registry.lower() == 'active' else 'history'}"
    delete_resp = context.client.delete(url)
    assert delete_resp.status_code in [200, 204]

@step('I create a digital order for "{product}" with email "{email}"') # type: ignore
def create_digital_order(context, product: str, email: str):
    payload = {"product": product, "email": email}
    post_resp = context.client.post(f"{context.base_url}/api/orders/digital", json=payload)

    assert post_resp.status_code == 201
    context.current_order = post_resp.json()

@then('The order should be present in {registry} registry') # type: ignore
def order_in_registry(context, registry: str):
    if not context.current_order:
        raise ValueError(f"No last order to reffer to.")
    if registry not in REGISTRIES:
        raise ValueError(f"Invalid registry: {registry}. Must be one of {REGISTRIES}.")

    url = f"{context.base_url}/api/orders/{'active' if registry == 'active' else 'history'}"
    get_resp = context.client.get(url)
    
    assert get_resp.status_code == 200
    orders_ids = [order.get('id') for order in get_resp.json()]

    assert context.current_order.get('id') in orders_ids

@then('The order should have a unique ID assigned') # type: ignore
def order_has_id(context):
    if not context.current_order:
        raise ValueError(f"No last order to reffer to.")
    assert context.current_order.get('id') != None

@step('The order status should be {status}') # type: ignore
def order_has_status(context, status):
    if not context.current_order:
        raise ValueError(f"No last order to reffer to.")
    if status not in STATUSES:
        raise ValueError(f"Invalid status: {status}. Must be one of {STATUSES}.")
    
    assert context.current_order.get("status") == status

@then('Number of orders in {registry} registry should be {count:d}') # type: ignore
def registry_count(context, registry, count):
    if registry not in REGISTRIES:
        raise ValueError(f"Invalid registry: {registry}. Must be one of {REGISTRIES}.")
    if not isinstance(count, int) or count < 0: 
        raise ValueError(f"Invalid count: {count}. Must be one an non negative integer.")

    url = f"{context.base_url}/api/orders/{'active' if registry == 'active' else 'history'}/count"
    get_resp = context.client.get(url)    

    assert get_resp.status_code == 200
    orders_count = get_resp.json().get("count")

    assert orders_count == count

@step('I create a physical order for "{product}" with email "{email}" and address:') # type: ignore
def create_physical_order(context, product, email):
    address = {row['field']: (None if row['value'] == "None" else row['value']) for row in context.table}
    payload = {"product": product, "email": email, "address": address}
    post_resp = context.client.post(f"{context.base_url}/api/orders/physical", json=payload)

    assert post_resp.status_code == 201
    context.current_order = post_resp.json()
    assert context.current_order.get("product") == product
    assert context.current_order.get("email") == email

@then('The order address should be:') # type: ignore
def match_address(context):
    if not context.current_order:
        raise ValueError(f"No last order to reffer to.")
    address = {row['field']: (None if row['value'] == "None" else row['value']) for row in context.table}

    url = f"{context.base_url}/api/order/{context.current_order.get('id')}"
    get_resp = context.client.get(url)

    assert get_resp.status_code == 200 
    order_address = get_resp.json().get("address")

    for key, value in address.items():
        assert value == order_address.get(key)

@when('I change the order email to "{email}"') # type: ignore
def change_email(context, email):
    if not context.current_order:
        raise ValueError(f"No last order to reffer to.")

    payload = {"email": email}
    url = f"{context.base_url}/api/order/{context.current_order.get('id')}/email"
    patch_resp = context.client.patch(url, json=payload)

    if patch_resp.status_code in [200, 204]:
        if patch_resp.status_code == 200:  
            order = patch_resp.json()
        else:
            url = f"{context.base_url}/api/order/{context.current_order.get('id')}"
            get_resp = context.client.get(url)

            assert get_resp.status_code == 200
            order = get_resp.json()

        assert email == order.get("email")
        context.current_order = order
    else:
        assert patch_resp.status_code == 422

@then('The order email should be "{email}"') # type: ignore
def match_email(context, email):
    if not context.current_order:
        raise ValueError(f"No last order to reffer to.")
    url = f"{context.base_url}/api/order/{context.current_order.get('id')}"
    get_resp = context.client.get(url)
    
    assert get_resp.status_code == 200
    order = get_resp.json()

    assert email == order.get("email")

@when('I change the order address to:') # type: ignore
def change_address(context):
    if not context.current_order:
        raise ValueError(f"No last order to reffer to.")
    address = {row['field']: (None if row['value'] == "None" else row['value']) for row in context.table}
    for key in ADDRESS_KEYS:
        if key not in address.keys():
            raise ValueError(f"Missing address key: {key}. All address keys neccessary: {ADDRESS_KEYS}.")

    payload = {"address": address}
    url = f"{context.base_url}/api/order/{context.current_order.get('id')}/address"
    patch_resp = context.client.patch(url, json=payload)

    if patch_resp.status_code in [200, 204]:
        if patch_resp.status_code == 200:
            order = patch_resp.json()
        else:
            url = f"{context.base_url}/api/order/{context.current_order.get('id')}"
            get_resp = context.client.get(url)

            assert get_resp.status_code == 200
            order = get_resp.json()
            
        order_address = order.get("address")
        for key, value in address.items():
            assert value == order_address.get(key)
        context.current_order = order
    else:
        assert patch_resp.status_code == 422

        
@given('The {registry} registry has 1 {order_type} order') # type: ignore
def populate_registry(context, registry, order_type):
    if order_type not in ORDER_TYPES:
        raise ValueError(f"Invalid order type: {order_type}. Must be one of {ORDER_TYPES}.")
    if registry not in REGISTRIES:
        raise ValueError(f"Invalid registry: {registry}. Must be one of {REGISTRIES}.")
    
    payload = {"product": PRODUCT, "email": EMAIL, "address": None}
    if order_type == "physical":
        payload["address"] = ADDRESS

    url = f"{context.base_url}/api/orders/{'digital' if order_type == 'digital' else 'physical'}"
    post_resp = context.client.post(url, json=payload)

    assert post_resp.status_code == 201
    order = post_resp.json()

    patch_resp = None
    if registry == "history":
        url = f"{context.base_url}/api/order/{order.get('id')}/advance"
        for _ in range(3):
            patch_resp = context.client.patch(url)
            assert patch_resp.status_code in [200, 204]

    if patch_resp and patch_resp.status_code == 200:
        order = patch_resp.json()
    else:
        url = f"{context.base_url}/api/order/{order.get('id')}"
        get_resp = context.client.get(url)

        assert get_resp.status_code == 200
        order = get_resp.json()
    
    context.current_order = order

@step('I cancel the order') # type: ignore
def cancel_order(context):
    if not context.current_order:
        raise ValueError(f"No last order to reffer to.")

    url = f"{context.base_url}/api/order/{context.current_order.get('id')}/cancel"
    patch_resp = context.client.patch(url)

    assert patch_resp.status_code in [200, 204]

    if patch_resp.status_code == 200:  
        order = patch_resp.json()
    else:
        url = f"{context.base_url}/api/order/{context.current_order.get('id')}"
        get_resp = context.client.get(url)

        assert get_resp.status_code == 200
        order = get_resp.json()

    context.current_order = order

@step('I advance the order status {count:d} times') # type: ignore
def advance_order(context, count):
    if not context.current_order:
        raise ValueError(f"No last order to reffer to.")
    if not isinstance(count, int) or count < 0: 
        raise ValueError(f"Invalid count: {count}. Must be one an non negative integer.")

    url = f"{context.base_url}/api/order/{context.current_order.get('id')}/advance"
    patch_resp = None
    for _ in range(count):
        patch_resp = context.client.patch(url)
        assert patch_resp.status_code in [200, 204]

    if patch_resp and patch_resp.status_code == 200:
        order = patch_resp.json()
    else:
        url = f"{context.base_url}/api/order/{context.current_order.get('id')}"
        get_resp = context.client.get(url)

        assert get_resp.status_code == 200
        order = get_resp.json()
    
    context.current_order = order

@step('I file a return') # type: ignore
def return_order(context):
    if not context.current_order:
        raise ValueError(f"No last order to reffer to.")
    
    url = f"{context.base_url}/api/order/{context.current_order.get('id')}/return"
    patch_resp = context.client.patch(url)

    assert patch_resp.status_code in [200, 204]

    if patch_resp.status_code == 200:
        order = patch_resp.json()
    else:
        url = f"{context.base_url}/api/order/{context.current_order.get('id')}"
        get_resp = context.client.get(url)

        assert get_resp.status_code == 200
        order = get_resp.json()
    
    context.current_order = order

@step('There are orders in the registry:') # type: ignore
def add_multiple_orders(context):
    orders = [{"product": row['product'], "email": row['email'], "type": row['type']} for row in context.table]
    
    for order in orders:
        if order.get("type") not in ORDER_TYPES:
            raise ValueError(f"Invalid order type: {order.get('type')}. Must be one of {ORDER_TYPES}.")

        url = f"{context.base_url}/api/orders/{'digital' if order.get('type') == 'digital' else 'physical'}"
        payload = {"product": order.get('product'), "email": order.get('email'), "address": ADDRESS}
        post_resp = context.client.post(url, json=payload)

        assert post_resp.status_code == 201

@step('I get orders for email "{email}"') # type: ignore
def get_by_email(context, email):
    safe_email = quote(email)

    url = f"{context.base_url}/api/orders/email/{safe_email}"
    get_resp = context.client.get(url)

    assert get_resp.status_code == 200
    context.results = get_resp.json()

@then('I should see {count:d} orders in the results') # type: ignore
def results_count(context, count):
    if not context.results:
        raise ValueError(f"No respresultsonse to reffer to.")
    if not isinstance(count, int) or count < 0: 
        raise ValueError(f"Invalid count: {count}. Must be one an non negative integer.")
    
    assert len(context.results) == count

@then('The results should contain products:') # type: ignore
def results_contain_products(context):
    if not context.results:
        raise ValueError(f"No results to reffer to.")
    
    products = [row["product"] for row in context.table]

    for prod in products:
        contains = any(res.get("product") == prod for res in context.results)
        assert contains

        assert contains == True
