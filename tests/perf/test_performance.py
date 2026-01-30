import requests
import pytest
from random import randint

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT_LIMIT = 0.2

class TestAPIPerformance:

    @pytest.fixture(autouse=True)
    def clear_registry(self):
        requests.delete(f"{BASE_URL}/orders/active")
        requests.delete(f"{BASE_URL}/orders/history")

    @pytest.mark.parametrize("amount", [
        (1),
        (100),
        (1000),
    ], ids=[
        "create single",
        "create 100",
        "create 1000",
    ])
    def test_create(self, amount: int):
        payload = {"product": "Enough Is Enough", "email": "enough@enough.net"}
        
        with requests.Session():
            for i in range(amount):
                post_resp = requests.post(f"{BASE_URL}/api/orders/digital", json=payload, timeout=TIMEOUT_LIMIT)
                assert post_resp.status_code == 201
                assert post_resp.elapsed.total_seconds() < TIMEOUT_LIMIT, f"Iteracja {i} przekroczyła limit"

    @pytest.mark.parametrize("amount", [
        (1),
        (100),
        (1000),
    ], ids=[
        "create and cancel single",
        "create and cancel 100",
        "create and cancel 1000",
    ])
    def test_cancel_random(self, amount: int):
        payload = {"product": "Enough Is Enough", "email": "enough@enough.net"}
        ids: list[str] = []

        with requests.Session():
            for _ in range(amount):
                post_resp = requests.post(f"{BASE_URL}/api/orders/digital", json=payload, timeout=TIMEOUT_LIMIT*2)
                assert post_resp.status_code == 201
                ids.append(post_resp.json().get('id'))

        with requests.Session():
            for i in range(amount):
                num = randint(0, len(ids)-1)
                id = ids.pop(num)

                patch_resp = requests.patch(f"{BASE_URL}/api/order/{id}/cancel", json=payload, timeout=TIMEOUT_LIMIT)
                assert patch_resp.status_code == 200
                assert patch_resp.elapsed.total_seconds() < TIMEOUT_LIMIT, f"Iteracja {i} przekroczyła limit"

    @pytest.mark.parametrize("amount", [
        (1),
        (100),
        (1000),
    ], ids=[
        "create and cancel single",
        "create and cancel 100",
        "create and cancel 1000",
    ])
    def test_random_cancel_or_advance(self, amount: int):
        payload = {"product": "Enough Is Enough", "email": "enough@enough.net"}
        ids: list[str] = []

        with requests.Session():
            for _ in range(amount):
                post_resp = requests.post(f"{BASE_URL}/api/orders/digital", json=payload, timeout=TIMEOUT_LIMIT*2)
                assert post_resp.status_code == 201
                ids.append(post_resp.json().get('id'))

        with requests.Session():
            for i in range(amount):
                num = randint(0, len(ids)-1)
                id = ids.pop(num)
                
                patch_resp = requests.patch(f"{BASE_URL}/api/order/{id}/{'advance' if randint(0,1) else 'cancel'}", json=payload, timeout=TIMEOUT_LIMIT)
                assert patch_resp.status_code == 200
                assert patch_resp.elapsed.total_seconds() < TIMEOUT_LIMIT, f"Iteracja {i} przekroczyła limit"























# def test_create_and_delete_100_accounts():
#     """Test: Tworzy (POST) i anuluje (PATCH) zamówienie 100 razy."""
#     email = "perf_test@example.com"
#     payload = {"product": "Digital Service", "email": email}
    
#     for i in range(100):
#         # 1. Tworzenie (ścieżka z Twojego kodu: /api/orders/digital)
#         r_create = requests.post(f"{BASE_URL}/api/orders/digital", json=payload, timeout=TIMEOUT_LIMIT)
#         assert r_create.status_code == 201
#         order_id = r_create.json().get("id")
        
#         # 2. Anulowanie (zmienione na PATCH i /api/order/<id>/cancel)
#         r_cancel = requests.patch(f"{BASE_URL}/api/order/{order_id}/cancel", timeout=TIMEOUT_LIMIT)
        
#         assert r_cancel.status_code == 200

# def test_account_processing_100_transfers():
#     """Test: Wykonuje 100 operacji advance, każda na nowym zamówieniu, aby uniknąć 404 po zakończeniu cyklu życia."""
#     email = "transfer_perf@example.com"
#     payload = {"product": "Bank Account", "email": email}
    
#     for i in range(100):
#         # 1. Setup - nowe zamówienie dla każdej iteracji
#         r_setup = requests.post(f"{BASE_URL}/api/orders/digital", json=payload, timeout=TIMEOUT_LIMIT)
#         order_id = r_setup.json().get("id")
        
#         # 2. Wykonanie advance
#         r_adv = requests.patch(f"{BASE_URL}/api/order/{order_id}/advance", timeout=TIMEOUT_LIMIT)
        
#         # Sprawdzamy czy przeszło (200) i czy było szybkie
#         assert r_adv.status_code == 200, f"Błąd w iteracji {i}: {r_adv.text}"

# def test_bulk_cleanup_1000_accounts():
#     """Tworzy 1000 i anuluje wszystkie (PATCH)."""
#     ids = []
#     email = "bulk@example.com"
    
#     for i in range(1000):
#         r = requests.post(f"{BASE_URL}/api/orders/digital", json={"product": f"P_{i}", "email": email})
#         ids.append(r.json().get("id"))
    
#     for order_id in ids:
#         # Zmienione na PATCH
#         r = requests.patch(f"{BASE_URL}/api/order/{order_id}/cancel")
#         assert r.status_code == 200