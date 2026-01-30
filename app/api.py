from flask import Flask, request, jsonify
from src.digital_order import DigitalOrder
from src.physical_order import PhysicalOrder
from src.order_registry import OrderRegistry
from src.custom_errors import OrderNotFoundError, ReturnPolicyViolation

def create_app():
    app = Flask(__name__)
    registry = OrderRegistry()

    @app.errorhandler(OrderNotFoundError)
    def handle_not_found(e):
        return jsonify({"error": str(e)}), 404

    @app.errorhandler(ReturnPolicyViolation)
    def handle_policy_violation(e):
        return jsonify({"error": str(e)}), 400

    @app.post("/api/orders/digital")
    def create_digital_order():
        data = request.get_json()
        order = DigitalOrder(data.get("product"), data.get("email"))
        if registry.add_order(order):
            return jsonify(order.__dict__), 201
        return jsonify({"error": "Invalid data"}), 422

    @app.post("/api/orders/physical")
    def create_physical_order():
        data = request.get_json()
        order = PhysicalOrder(data.get("product"), data.get("email"), data.get("address"))
        if registry.add_order(order):
            return jsonify(order.__dict__), 201
        return jsonify({"error": "Invalid data"}), 422

    @app.get("/api/orders/active")
    def get_all_active_orders():
        return jsonify([o.__dict__ for o in registry.get_active_orders()]), 200

    @app.get("/api/orders/active/count")
    def get_all_active_orders_count():
        return jsonify({"count": registry.get_active_orders_count()}), 200

    @app.delete("/api/orders/active")
    def clear_active():
        registry.active_registry.clear()
        return jsonify({"message": "Active registry cleared"}), 200

    @app.get("/api/orders/history")
    def get_all_history_orders():
        return jsonify([o.__dict__ for o in registry.get_history_orders()]), 200

    @app.get("/api/orders/history/count")
    def get_all_history_orders_count():
        return jsonify({"count": registry.get_history_orders_count()}), 200

    @app.delete("/api/orders/history")
    def clear_history():
        registry.history_registry.clear()
        return jsonify({"message": "History registry cleared"}), 200

    @app.get("/api/order/<string:order_id>")
    def get_order(order_id):
        order = registry.get_order(order_id)
        if order:
            return jsonify(order.__dict__), 200
        return jsonify({"error": "Order not found"}), 404

    @app.patch("/api/order/<string:order_id>/cancel")
    def cancel_order(order_id):
        if registry.cancel_order(order_id):
            order = registry.get_order(order_id)
            return jsonify(order.__dict__), 200
        return jsonify({"error": "Cannot cancel"}), 400

    @app.patch("/api/order/<string:order_id>/advance")
    def advance_order(order_id):
        updated_order = registry.advance_order(order_id)
        if updated_order:
            return jsonify(updated_order.__dict__), 200
        return jsonify({"error": "Order not found"}), 404

    @app.patch("/api/order/<string:order_id>/return")
    def return_order(order_id):
        if registry.return_order(order_id):
            order = registry.get_order(order_id)
            return jsonify(order.__dict__), 200
        return jsonify({"error": "Unknown error"}), 500

    @app.patch("/api/order/<string:order_id>/email")
    def update_email(order_id):
        data = request.get_json()
        if registry.update_email(order_id, data.get("email")):
            order = registry.get_order(order_id)
            return jsonify(order.__dict__), 200
        return jsonify({"error": "Update failed"}), 422

    @app.patch("/api/order/<string:order_id>/address")
    def update_address(order_id):
        data = request.get_json()
        if registry.update_address(order_id, data.get("address")):
            order = registry.get_order(order_id)
            return jsonify(order.__dict__), 200
        return jsonify({"error": "Update failed"}), 422
    
    @app.get("/api/orders/email/<path:email>")
    def get_email_orders(email):
        orders = registry.get_orders_by_email(email)
        return jsonify([o.__dict__ for o in orders]), 200

    return app