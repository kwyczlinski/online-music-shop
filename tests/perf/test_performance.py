import requests
import pytest
from random import randint, shuffle
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT_LIMIT = 0.4
MAX_WORKERS = 8

class TestAPIResponseTime:

    @pytest.fixture(autouse=True)
    def clear_registry(self):
        requests.delete(f"{BASE_URL}/orders/active")
        requests.delete(f"{BASE_URL}/orders/history")

    @pytest.fixture()
    def payload(self):
        return {"product": "Enough Is Enough", "email": "enough@enough.net"}

    @pytest.mark.parametrize("amount", [
        (1),
        (100),
        (1000),
    ], ids=[
        "create single",
        "create 100",
        "create 1000",
    ])
    def test_create(self, payload: dict[str, str], amount: int):
        with requests.Session() as session:
            def create_order(_):
                try:
                    return session.post(
                        f"{BASE_URL}/api/orders/digital", 
                        json=payload, 
                        timeout=TIMEOUT_LIMIT
                    )
                
                except requests.exceptions.RequestException as e:
                    return e
                
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                results = list(executor.map(create_order, range(amount)))

        success_count = sum(
            1 for res in results 
            if isinstance(res, requests.Response) 
            and res.status_code == 201
            and res.elapsed.total_seconds() < TIMEOUT_LIMIT
        )

        assert success_count >= amount * 0.95, f"Only {success_count}/{amount} requests returned within the timeout limit: {TIMEOUT_LIMIT}"

    @pytest.mark.parametrize("amount", [
        (1),
        (100),
        (1000),
    ], ids=[
        "create and cancel single",
        "create and cancel 100",
        "create and cancel 1000",
    ])
    def test_cancel_random(self, payload: dict[str, str], amount: int):

        with requests.Session() as session:
            def create_order(_):
                try:
                    return session.post(
                        f"{BASE_URL}/api/orders/digital", 
                        json=payload, 
                        timeout=TIMEOUT_LIMIT*2
                    ).json().get('id')
                
                except requests.exceptions.RequestException as e:
                    return e
            
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                ids = list(executor.map(create_order, range(amount)))

        shuffle(ids)

        with requests.Session() as session:
            def cancel_order(order_id):
                try:
                    patch_resp = session.patch(
                        f"{BASE_URL}/api/order/{order_id}/cancel", 
                        json=payload, 
                        timeout=TIMEOUT_LIMIT
                    )
                    return patch_resp
                
                except requests.exceptions.RequestException as e:
                    return e
                
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                results = list(executor.map(cancel_order, ids))

        success_count = sum(
            1 for res in results 
            if isinstance(res, requests.Response) 
            and res.status_code == 200 
            and res.elapsed.total_seconds() < TIMEOUT_LIMIT
        )

        assert success_count >= amount * 0.95, f"Only {success_count}/{amount} requests returned within the timeout limit: {TIMEOUT_LIMIT}"

    @pytest.mark.parametrize("amount", [
        (1),
        (100),
        (1000),
    ], ids=[
        "create and cancel single",
        "create and cancel 100",
        "create and cancel 1000",
    ])
    def test_random_cancel_or_advance(self, payload: dict[str, str], amount: int):

        with requests.Session() as session:
            def create_order(_):
                try:
                    return session.post(
                        f"{BASE_URL}/api/orders/digital", 
                        json=payload, 
                        timeout=TIMEOUT_LIMIT*2
                    ).json().get('id')
                
                except requests.exceptions.RequestException as e:
                    return e
                
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                ids = list(executor.map(create_order, range(amount)))

        tasks = [(order_id, "advance" if randint(0, 1) else "cancel") for order_id in ids]
        shuffle(tasks)

        with requests.Session() as session:
            def cancel_or_advance_order(task):
                order_id, action = task
                try:
                    return session.patch(
                        f"{BASE_URL}/api/order/{order_id}/{action}", 
                        json=payload, 
                        timeout=TIMEOUT_LIMIT
                    )
                
                except requests.exceptions.RequestException as e:
                    return e
                
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                results = list(executor.map(cancel_or_advance_order, tasks))

        success_count = sum(
            1 for res in results 
            if isinstance(res, requests.Response) 
            and res.status_code == 200 
            and res.elapsed.total_seconds() < TIMEOUT_LIMIT
        )

        assert success_count >= amount * 0.95, f"Only {success_count}/{amount} requests returned within the timeout limit: {TIMEOUT_LIMIT}"
