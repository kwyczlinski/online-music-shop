import requests

def before_scenario(context, scenario):
    context.base_url = "http://127.0.0.1:5000"
    
    context.client = requests.Session()

    # czyszczenie registry pomiędzy testami
    context.client.delete(f"{context.base_url}/api/orders/active")
    context.client.delete(f"{context.base_url}/api/orders/history")